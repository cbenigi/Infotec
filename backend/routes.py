from html_pdf_generator import HTMLPDFGenerator
from html_orden_generator import HTMLOrdenGenerator
from flask_mail import Mail, Message
from flask import Blueprint, request, jsonify, session, send_from_directory, current_app, send_file, render_template
import os
from werkzeug.utils import secure_filename
from models import (
    db,
    User,
    Empresa,
    Cliente,
    Visita,
    Zona,
    Cotizacion,
    CotizacionItem,
    OrdenCompra,
    OrdenCompraItem,
    Proveedor,
    EmpresaAcceso,
    EmpresaNominaRelacion
)
from sqlalchemy import or_
from werkzeug.security import check_password_hash
from datetime import datetime
import traceback
import re

# Inicializar Mail
mail = Mail()

routes = Blueprint('routes', __name__)

def _parse_float(value):
    if value is None:
        return None
    try:
        if isinstance(value, str):
            value = value.replace(',', '.')
        return float(value)
    except (ValueError, TypeError):
        return None

def _generar_consecutivo_orden():
    ultima_orden = OrdenCompra.query.order_by(OrdenCompra.id.desc()).first()
    numero = 1
    if ultima_orden and ultima_orden.numero:
        match = re.search(r'(\d+)$', ultima_orden.numero)
        if match:
            try:
                numero = int(match.group(1)) + 1
            except ValueError:
                numero = ultima_orden.id + 1
    return f"OC-{numero:04d}"

def _obtener_empresa_actual(user_id):
    if not user_id:
        return None
    return Empresa.query.filter_by(user_id=user_id).first()

def _resolver_nombre_comprador(comprador_tipo, comprador_id):
    if comprador_tipo == 'cliente':
        cliente = Cliente.query.get(comprador_id)
        return cliente.nombre if cliente else 'Cliente no disponible'
    empresa = Empresa.query.get(comprador_id)
    return empresa.nombre if empresa else 'Empresa no disponible'

def _calcular_total_estimado(items):
    total = 0.0
    for item in items:
        cantidad_valor = _parse_float(item.cantidad if hasattr(item, 'cantidad') else item.get('cantidad'))
        precio = item.precio_unitario if hasattr(item, 'precio_unitario') else _parse_float(item.get('precio_unitario'))
        if cantidad_valor is not None and precio:
            total += cantidad_valor * precio
    return round(total, 2)

def _calcular_totales(data, items):
    iva_rate = 0.19
    subtotal_input = _parse_float(data.get('subtotal')) if isinstance(data, dict) else None
    total_input = _parse_float(data.get('total')) if isinstance(data, dict) else None
    items_total = _calcular_total_estimado(items) if items else 0.0

    if subtotal_input and subtotal_input > 0:
        subtotal = subtotal_input
        iva_valor = round(subtotal * iva_rate, 2)
        total = round(subtotal + iva_valor, 2)
    elif total_input and total_input > 0:
        total = total_input
        subtotal = round(total / (1 + iva_rate), 2)
        iva_valor = round(total - subtotal, 2)
    elif items_total > 0:
        subtotal = round(items_total, 2)
        iva_valor = round(subtotal * iva_rate, 2)
        total = round(subtotal + iva_valor, 2)
    else:
        subtotal = iva_valor = total = 0.0

    return subtotal, iva_valor, total

def _serialize_empresa(empresa, current_user_id=None, es_compartida=False):
    owner = empresa.user
    return {
        'id': empresa.id,
        'nombre': empresa.nombre,
        'nit': empresa.nit,
        'telefono': empresa.telefono,
        'correo': empresa.correo,
        'direccion': empresa.direccion,
        'logo_url': empresa.logo_url,
        'owner_id': empresa.user_id,
        'owner_nombre': owner.nombre if owner else None,
        'owner_email': owner.email if owner else None,
        'es_propietario': current_user_id is not None and empresa.user_id == current_user_id,
        'es_compartida': es_compartida
    }

def _usuario_tiene_acceso_empresa(user_id, empresa_id):
    if not user_id:
        return False
    if Empresa.query.filter_by(id=empresa_id, user_id=user_id).first():
        return True
    return EmpresaNominaRelacion.query.filter_by(empresa_id=empresa_id, user_id=user_id).first() is not None

@routes.after_request
def add_cors_headers(response):
    # Asegurar headers CORS en todas las respuestas del blueprint
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Vary'] = 'Origin'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response

@routes.errorhandler(Exception)
def handle_exception(e):
    print(f"ERROR: {str(e)}")
    print(f"TRACEBACK: {traceback.format_exc()}")
    return jsonify({'message': f'Error interno: {str(e)}'}), 500

# @routes.before_request
# def log_request_info():
#     print(f"REQUEST: {request.method} {request.path}")
#     print(f"HEADERS: {dict(request.headers)}")
#     print(f"CONTENT_TYPE: {request.content_type}")
#     if request.is_json:
#         print(f"JSON_DATA: {request.get_json()}")
#     else:
#         print(f"FORM_DATA: {request.form}")
#         print(f"RAW_DATA: {request.get_data()}")

# Autenticación básica
@routes.route('/login', methods=['POST', 'OPTIONS'])
def login():
    # Responder preflight CORS
    if request.method == 'OPTIONS':
        return ('', 200)
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        session['user_id'] = user.id
        session['rol'] = user.rol
        return jsonify({'message': 'Login exitoso', 'rol': user.rol}), 200
    return jsonify({'message': 'Credenciales inválidas'}), 401

@routes.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout exitoso'}), 200

# CRUD Usuarios (solo admin)
@routes.route('/usuarios', methods=['GET'])
def get_usuarios():
    # Temporalmente permitir acceso sin autenticación para desarrollo
    # if session.get('rol') != 'admin':
    #     return jsonify({'message': 'Acceso denegado'}), 403
    usuarios = User.query.all()
    return jsonify([{'id': u.id, 'nombre': u.nombre, 'email': u.email, 'rol': u.rol} for u in usuarios]), 200

@routes.route('/test', methods=['GET', 'POST'])
def test_endpoint():
    print("=== TEST ENDPOINT CALLED ===")
    return jsonify({'message': 'Test endpoint working', 'method': request.method}), 200

@routes.route('/usuarios', methods=['POST'])
def create_usuario():
    try:
        if not request.json:
            return jsonify({'message': 'No se recibieron datos'}), 400
        
        data = request.json
        rol = data.get('rol', 'aseo')
        if rol not in ('aseo', 'nomina', 'admin', 'supervisor', 'tecnico'):
            return jsonify({'message': 'Rol inválido'}), 400

        # Validar campos requeridos
        required_fields = ['nombre', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'El campo {field} es requerido'}), 400
        
        # Verificar si el email ya existe
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'message': 'El email ya está registrado'}), 400
        
        # Crear usuario
        user = User(nombre=data['nombre'], email=data['email'], rol=rol)
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        # Iniciar sesión
        session['user_id'] = user.id
        session['rol'] = user.rol
        
        return jsonify({
            'message': 'Usuario creado y sesión iniciada',
            'rol': user.rol,
            'nombre': user.nombre
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error interno: {str(e)}'}), 500

@routes.route('/usuarios/<int:id>', methods=['PUT', 'DELETE'])
def manage_usuario(id):
    if session.get('rol') != 'admin':
        return jsonify({'message': 'Acceso denegado'}), 403
    user = User.query.get_or_404(id)
    if request.method == 'PUT':
        data = request.json
        user.nombre = data['nombre']
        user.email = data['email']
        if 'password' in data:
            user.set_password(data['password'])
        db.session.commit()
        return jsonify({'message': 'Usuario actualizado'}), 200
    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Usuario eliminado'}), 200

# CRUD Empresa
@routes.route('/empresa', methods=['GET', 'OPTIONS'])
def get_empresa():
    if request.method == 'OPTIONS':
        return ('', 200)

    # Permitir user_id por query para diagnóstico/fallback
    q_user_id = request.args.get('user_id', type=int)
    user_id = q_user_id or session.get('user_id')
    if not user_id:
        return jsonify({'message': 'No autenticado'}), 401

    empresa = Empresa.query.filter_by(user_id=user_id).first()
    if not empresa:
        return jsonify({'exists': False}), 200
    
    return jsonify({
        'exists': True,
        **_serialize_empresa(empresa, current_user_id=user_id)
    }), 200

@routes.route('/empresa', methods=['POST', 'OPTIONS'])
def create_empresa():
    if request.method == 'OPTIONS':
        return ('', 200)

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'No autenticado'}), 401
    
    # Verificar que no tenga empresa ya
    existing = Empresa.query.filter_by(user_id=user_id).first()
    if existing:
        return jsonify({'message': 'Ya tienes una empresa registrada'}), 400
    
    data = request.json
    empresa = Empresa(
        user_id=user_id,
        nombre=data['nombre'],
        nit=data['nit'],
        telefono=data['telefono'],
        correo=data['correo'],
        direccion=data.get('direccion', ''),
        logo_url=data.get('logo_url', '')
    )
    db.session.add(empresa)
    db.session.commit()
    return jsonify({'message': 'Empresa creada exitosamente', 'id': empresa.id}), 201

@routes.route('/empresa', methods=['PUT', 'OPTIONS'])
def update_empresa():
    if request.method == 'OPTIONS':
        return ('', 200)

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'No autenticado'}), 401
    
    empresa = Empresa.query.filter_by(user_id=user_id).first()
    if not empresa:
        return jsonify({'message': 'No tienes una empresa registrada'}), 404
    
    data = request.json
    empresa.nombre = data.get('nombre', empresa.nombre)
    empresa.nit = data.get('nit', empresa.nit)
    empresa.telefono = data.get('telefono', empresa.telefono)
    empresa.correo = data.get('correo', empresa.correo)
    empresa.direccion = data.get('direccion', empresa.direccion)
    if 'logo_url' in data:
        empresa.logo_url = data['logo_url']
    
    db.session.commit()
    return jsonify({'message': 'Empresa actualizada exitosamente'}), 200

@routes.route('/empresas', methods=['GET', 'POST', 'OPTIONS'])
def manage_empresas_multiple():
    if request.method == 'OPTIONS':
        return ('', 200)

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'No autenticado'}), 401

    if session.get('rol') != 'nomina':
        return jsonify({'message': 'Acceso restringido a rol nómina'}), 403

    if request.method == 'GET':
        propias = Empresa.query.filter_by(user_id=user_id).order_by(Empresa.id.desc()).all()
        relaciones = EmpresaNominaRelacion.query.filter_by(user_id=user_id).all()
        data = [_serialize_empresa(e, current_user_id=user_id) for e in propias]
        propias_ids = {e.id for e in propias}
        for rel in relaciones:
            if rel.empresa_id in propias_ids or not rel.empresa:
                continue
            data.append(_serialize_empresa(rel.empresa, current_user_id=user_id, es_compartida=True))
        return jsonify(data), 200

    data = request.json or {}
    required = ['nombre', 'nit', 'telefono', 'correo']
    for field in required:
        if not data.get(field):
            return jsonify({'message': f'El campo {field} es requerido'}), 400

    empresa = Empresa(
        user_id=user_id,
        nombre=data['nombre'].strip(),
        nit=data['nit'].strip(),
        telefono=data['telefono'].strip(),
        correo=data['correo'].strip(),
        direccion=data.get('direccion', '').strip(),
        logo_url=data.get('logo_url', '').strip()
    )
    db.session.add(empresa)
    db.session.commit()
    return jsonify({'message': 'Empresa creada', 'empresa': _serialize_empresa(empresa)}), 201

@routes.route('/empresas/<int:empresa_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def update_or_delete_empresa(empresa_id):
    if request.method == 'OPTIONS':
        return ('', 200)

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'No autenticado'}), 401

    if session.get('rol') != 'nomina':
        return jsonify({'message': 'Acceso restringido a rol nómina'}), 403

    empresa = Empresa.query.filter_by(id=empresa_id, user_id=user_id).first()
    if not empresa:
        return jsonify({'message': 'Empresa no encontrada'}), 404

    try:
        if request.method == 'PUT':
            data = request.json or {}
            for field in ['nombre', 'nit', 'telefono', 'correo', 'direccion', 'logo_url']:
                if field in data:
                    setattr(empresa, field, data[field])
            db.session.commit()
            return jsonify({'message': 'Empresa actualizada', 'empresa': _serialize_empresa(empresa)}), 200
        else:
            db.session.delete(empresa)
            db.session.commit()
            return jsonify({'message': 'Empresa eliminada'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al procesar la empresa: {str(e)}'}), 500

@routes.route('/empresas/buscar', methods=['GET'])
def buscar_empresa_por_nit():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'No autenticado'}), 401

    nit = (request.args.get('nit') or '').strip()
    if not nit:
        return jsonify({'message': 'El parámetro nit es requerido'}), 400

    empresa = Empresa.query.filter_by(nit=nit).first()
    if not empresa:
        return jsonify({'found': False}), 200

    tiene_acceso = _usuario_tiene_acceso_empresa(user_id, empresa.id)
    solicitud_pendiente = EmpresaAcceso.query.filter_by(
        empresa_id=empresa.id,
        solicitante_id=user_id,
        estado='pendiente'
    ).first() is not None

    owner = empresa.user

    return jsonify({
        'found': True,
        'empresa': _serialize_empresa(empresa, current_user_id=user_id),
        'owner': {
            'id': owner.id if owner else None,
            'nombre': owner.nombre if owner else 'Propietario no disponible',
            'email': owner.email if owner else ''
        },
        'tiene_acceso': tiene_acceso,
        'solicitud_pendiente': solicitud_pendiente
    }), 200

@routes.route('/empresas/<int:empresa_id>/solicitudes', methods=['POST', 'OPTIONS'])
def solicitar_acceso_empresa(empresa_id):
    if request.method == 'OPTIONS':
        return ('', 200)

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'No autenticado'}), 401
    if session.get('rol') != 'nomina':
        return jsonify({'message': 'Solo usuarios de nómina pueden solicitar acceso'}), 403

    empresa = Empresa.query.get_or_404(empresa_id)
    if empresa.user_id == user_id:
        return jsonify({'message': 'Ya eres propietario de esta empresa'}), 400

    if _usuario_tiene_acceso_empresa(user_id, empresa.id):
        return jsonify({'message': 'Ya tienes acceso a esta empresa'}), 200

    existing = EmpresaAcceso.query.filter_by(
        empresa_id=empresa.id,
        solicitante_id=user_id,
        estado='pendiente'
    ).first()
    if existing:
        return jsonify({'message': 'Ya existe una solicitud pendiente para esta empresa'}), 200

    data = request.json or {}
    mensaje = (data.get('mensaje') or '').strip() or None

    solicitud = EmpresaAcceso(
        empresa_id=empresa.id,
        solicitante_id=user_id,
        mensaje=mensaje
    )
    db.session.add(solicitud)
    db.session.commit()

    return jsonify({
        'message': 'Solicitud enviada',
        'solicitud_id': solicitud.id
    }), 201

@routes.route('/empresa/solicitudes', methods=['GET', 'OPTIONS'])
def obtener_solicitudes_empresas():
    if request.method == 'OPTIONS':
        return ('', 200)

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'No autenticado'}), 401

    # Solo propietarios (aseo/admin) pueden ver solicitudes de sus empresas
    empresas_propias = Empresa.query.filter_by(user_id=user_id).all()
    if not empresas_propias:
        return jsonify([]), 200

    empresa_ids = [e.id for e in empresas_propias]
    solicitudes = EmpresaAcceso.query.filter(
        EmpresaAcceso.empresa_id.in_(empresa_ids),
        EmpresaAcceso.estado == 'pendiente'
    ).order_by(EmpresaAcceso.creado_en.asc()).all()

    result = []
    for sol in solicitudes:
        result.append({
            'id': sol.id,
            'estado': sol.estado,
            'mensaje': sol.mensaje,
            'creado_en': sol.creado_en.isoformat() if sol.creado_en else None,
            'empresa': _serialize_empresa(sol.empresa, current_user_id=user_id) if sol.empresa else None,
            'solicitante': {
                'id': sol.solicitante.id if sol.solicitante else None,
                'nombre': sol.solicitante.nombre if sol.solicitante else 'Usuario no disponible',
                'email': sol.solicitante.email if sol.solicitante else ''
            }
        })

    return jsonify(result), 200

@routes.route('/empresa/solicitudes/<int:solicitud_id>', methods=['PUT', 'OPTIONS'])
def resolver_solicitud_empresa(solicitud_id):
    if request.method == 'OPTIONS':
        return ('', 200)

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'No autenticado'}), 401

    solicitud = EmpresaAcceso.query.get_or_404(solicitud_id)
    if not solicitud.empresa or solicitud.empresa.user_id != user_id:
        return jsonify({'message': 'No autorizado para gestionar esta solicitud'}), 403

    data = request.json or {}
    accion = (data.get('accion') or '').lower()
    if accion not in ('aprobar', 'rechazar'):
        return jsonify({'message': 'Acción inválida'}), 400

    try:
        if accion == 'aprobar':
            solicitud.estado = 'aprobado'
            if not _usuario_tiene_acceso_empresa(solicitud.solicitante_id, solicitud.empresa_id):
                relacion = EmpresaNominaRelacion(
                    empresa_id=solicitud.empresa_id,
                    user_id=solicitud.solicitante_id
                )
                db.session.add(relacion)
        else:
            solicitud.estado = 'rechazado'

        db.session.commit()
        return jsonify({'message': f'Solicitud {accion}ada correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al actualizar la solicitud: {str(e)}'}), 500

# CRUD Clientes
# CRUD Proveedores
@routes.route('/proveedores', methods=['GET', 'OPTIONS'])
def get_proveedores():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        proveedores = Proveedor.query.order_by(Proveedor.nombre_comercial.asc()).all()
        return jsonify([{
            'id': p.id,
            'nombre_comercial': p.nombre_comercial,
            'nit': p.nit,
            'direccion': p.direccion,
            'tipo_insumos': p.tipo_insumos
        } for p in proveedores]), 200
    except Exception as e:
        return jsonify({'message': f'Error al obtener proveedores: {str(e)}'}), 500

@routes.route('/proveedores', methods=['POST', 'OPTIONS'])
def create_proveedor():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        data = request.json or {}
        required = ['nombre_comercial', 'nit']
        for field in required:
            if not data.get(field):
                return jsonify({'message': f'El campo {field} es requerido'}), 400
        proveedor = Proveedor(
            nombre_comercial=data['nombre_comercial'].strip(),
            nit=data['nit'].strip(),
            direccion=data.get('direccion', '').strip(),
            tipo_insumos=data.get('tipo_insumos', '').strip()
        )
        db.session.add(proveedor)
        db.session.commit()
        return jsonify({'message': 'Proveedor creado', 'id': proveedor.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al crear proveedor: {str(e)}'}), 500

@routes.route('/proveedores/<int:id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def manage_proveedor(id):
    if request.method == 'OPTIONS':
        return ('', 200)
    proveedor = Proveedor.query.get_or_404(id)
    try:
        if request.method == 'PUT':
            data = request.json or {}
            proveedor.nombre_comercial = data.get('nombre_comercial', proveedor.nombre_comercial).strip()
            proveedor.nit = data.get('nit', proveedor.nit).strip()
            proveedor.direccion = data.get('direccion', proveedor.direccion).strip()
            proveedor.tipo_insumos = data.get('tipo_insumos', proveedor.tipo_insumos).strip()
            db.session.commit()
            return jsonify({'message': 'Proveedor actualizado'}), 200
        else:
            db.session.delete(proveedor)
            db.session.commit()
            return jsonify({'message': 'Proveedor eliminado'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al procesar proveedor: {str(e)}'}), 500

@routes.route('/clientes', methods=['GET'])
def get_clientes():
    # Obtener el ID del usuario de la sesión
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'No autorizado'}), 401
    
    # Obtener el rol del usuario
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    # Si es admin, puede ver todos los clientes
    if user.rol == 'admin':
        clientes = Cliente.query.all()
    else:
        # Si no es admin, solo puede ver clientes de su empresa
        # Por ahora, mostrar todos (esto se puede refinar según la lógica de negocio)
        clientes = Cliente.query.all()
    
    return jsonify([{'id': c.id, 'nit': c.nit, 'nombre': c.nombre, 'administrador': c.administrador, 'correo': c.correo, 'tipo_codigo': c.tipo_codigo, 'logo_url': c.logo_url} for c in clientes]), 200

@routes.route('/clientes', methods=['POST'])
def create_cliente():
    data = request.json
    cliente = Cliente(nit=data['nit'], nombre=data['nombre'], administrador=data['administrador'], correo=data['correo'], tipo_codigo=data['tipo_codigo'], logo_url=data.get('logo_url', ''))
    db.session.add(cliente)
    db.session.commit()
    return jsonify({'message': 'Cliente creado'}), 201

@routes.route('/clientes/<int:id>', methods=['PUT', 'DELETE'])
def manage_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'PUT':
        data = request.json
        cliente.nit = data['nit']
        cliente.nombre = data['nombre']
        cliente.administrador = data['administrador']
        cliente.correo = data['correo']
        cliente.tipo_codigo = data['tipo_codigo']
        if 'logo_url' in data:
            cliente.logo_url = data['logo_url']
        db.session.commit()
        return jsonify({'message': 'Cliente actualizado'}), 200
    elif request.method == 'DELETE':
        db.session.delete(cliente)
        db.session.commit()
        return jsonify({'message': 'Cliente eliminado'}), 200

# CRUD Visitas



# Upload de imágenes
@routes.route('/upload', methods=['POST', 'OPTIONS'])
def upload_file():
    # Preflight CORS
    if request.method == 'OPTIONS':
        return ('', 200)

    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    # Validación/normalización de extensión y MIME
    allowed_ext = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
    mime_to_ext = {
        'image/png': '.png',
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/webp': '.webp',
        'image/gif': '.gif'
    }

    original_name = file.filename
    name_lower = (original_name or '').lower()
    base, ext = os.path.splitext(name_lower)

    # Si la extensión no es válida, intenta por MIME; si no, por defecto .jpg
    if ext not in allowed_ext:
        guessed_ext = mime_to_ext.get((file.mimetype or '').lower())
        ext = guessed_ext if guessed_ext in allowed_ext else '.jpg'

    safe_base = secure_filename(base) or 'image'
    # Evitar colisiones
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    filename = f"{safe_base}_{timestamp}{ext}"

    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    return jsonify({'url': f'/uploads/{filename}'}), 200

@routes.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# CRUD Visitas
@routes.route('/visita', methods=['POST'])
def create_visita():
    try:
        data = request.json
        # Generar ID automático secuencial
        fecha = datetime.strptime(data['fecha'], '%Y-%m-%d')
        
        # Buscar la última visita para generar secuencial
        ultima_visita = Visita.query.order_by(Visita.id.desc()).first()
        
        # Generar el siguiente número secuencial
        if ultima_visita:
            # Intentar extraer el número del ID (puede ser solo números o tener formato antiguo)
            try:
                # Si el ID tiene formato "AL-0001" o "31102025-AL-1539"
                if '-' in ultima_visita.id:
                    ultimo_numero = int(ultima_visita.id.split('-')[-1])
                else:
                    # Si el ID es solo números
                    ultimo_numero = int(ultima_visita.id)
                siguiente_numero = ultimo_numero + 1
            except (ValueError, AttributeError):
                siguiente_numero = 1
        else:
            siguiente_numero = 1
        
        # Formato: solo números con padding a 4 dígitos
        visita_id = f"{siguiente_numero:04d}"
        
        # Procesar hora si se proporciona
        hora = None
        if data.get('hora'):
            hora = datetime.strptime(data['hora'], '%H:%M').time()

        # Resolver empresa del usuario en sesión (si existe)
        empresa_id = None
        user_id = session.get('user_id')
        print(f"DEBUG: Creando visita - user_id en sesión: {user_id}", flush=True)
        if user_id:
            emp = Empresa.query.filter_by(user_id=user_id).first()
            print(f"DEBUG: Empresa encontrada para user_id {user_id}: {emp.id if emp else 'None'}", flush=True)
            if emp:
                empresa_id = emp.id
        
        print(f"DEBUG: empresa_id asignada: {empresa_id}", flush=True)
        
        visita = Visita(
            id=visita_id,
            fecha=fecha,
            hora=hora,
            supervisor_id=data['supervisor_id'],
            cliente_id=data['cliente_id'],
            empresa_id=empresa_id,
            conclusiones=data.get('conclusiones', '')
        )
        
        db.session.add(visita)
        db.session.flush()  # Para obtener el ID
        
        # Agregar zonas
        for zona_data in data.get('zonas', []):
            zona = Zona(
                visita_id=visita.id,
                seccion=zona_data['seccion'],
                concepto_actividad=zona_data['concepto_actividad'],
                calificacion=zona_data['calificacion'],
                observaciones=zona_data.get('observaciones', ''),
                foto_url=zona_data.get('foto_url', '')
            )
            db.session.add(zona)
        
        db.session.commit()
        
        # Enviar informe automáticamente al cliente y a solamysas@gmail.com
        try:
            cliente = Cliente.query.get(data['cliente_id'])
            if cliente and cliente.correo:
                emails = [cliente.correo.strip(), 'solamysas@gmail.com']
                print(f"DEBUG: Enviando informe automático a: {emails}", flush=True)
                _enviar_informe_email(visita.id, emails)
        except Exception as email_err:
            print(f"ERROR: No se pudo enviar el informe automático: {str(email_err)}", flush=True)
            # No fallar la creación de la visita si falla el correo
            
        return jsonify({'message': 'Visita creada exitosamente', 'id': visita.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al crear visita: {str(e)}'}), 500

@routes.route('/visita/<string:visita_id>', methods=['GET'])
def get_visita(visita_id):
    try:
        visita = Visita.query.get_or_404(visita_id)
        return jsonify({
            'id': visita.id,
            'fecha': visita.fecha.strftime('%Y-%m-%d'),
            'hora': visita.hora.strftime('%H:%M') if visita.hora else None,
            'supervisor_id': visita.supervisor_id,
            'cliente_id': visita.cliente_id,
            'conclusiones': visita.conclusiones,
            'supervisor': {'nombre': visita.supervisor.nombre},
            'cliente': {'nombre': visita.cliente.nombre},
            'zonas': [{
                'id': zona.id,
                'seccion': zona.seccion,
                'concepto_actividad': zona.concepto_actividad,
                'calificacion': zona.calificacion,
                'observaciones': zona.observaciones,
                'foto_url': zona.foto_url
            } for zona in visita.zonas]
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error al obtener visita: {str(e)}'}), 500

@routes.route('/visita/<string:visita_id>', methods=['PUT'])
def update_visita(visita_id):
    try:
        visita = Visita.query.get_or_404(visita_id)
        data = request.json
        
        visita.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d')
        # Procesar hora si se proporciona
        if data.get('hora'):
            visita.hora = datetime.strptime(data['hora'], '%H:%M').time()
        else:
            visita.hora = None
        visita.supervisor_id = data['supervisor_id']
        visita.cliente_id = data['cliente_id']
        visita.conclusiones = data.get('conclusiones', '')

        # Asegurar empresa_id
        if not visita.empresa_id:
            user_id = session.get('user_id')
            if user_id:
                emp = Empresa.query.filter_by(user_id=user_id).first()
                if emp:
                    visita.empresa_id = emp.id
        
        # Eliminar zonas existentes
        Zona.query.filter_by(visita_id=visita_id).delete()
        
        # Agregar nuevas zonas
        for zona_data in data.get('zonas', []):
            zona = Zona(
                visita_id=visita.id,
                seccion=zona_data['seccion'],
                concepto_actividad=zona_data['concepto_actividad'],
                calificacion=zona_data['calificacion'],
                observaciones=zona_data.get('observaciones', ''),
                foto_url=zona_data.get('foto_url', '')
            )
            db.session.add(zona)
        
        db.session.commit()
        return jsonify({'message': 'Visita actualizada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al actualizar visita: {str(e)}'}), 500

@routes.route('/visita/<string:visita_id>', methods=['DELETE'])
def delete_visita(visita_id):
    try:
        visita = Visita.query.get_or_404(visita_id)
        
        # Eliminar zonas asociadas primero
        Zona.query.filter_by(visita_id=visita_id).delete()
        
        # Eliminar la visita
        db.session.delete(visita)
        db.session.commit()
        
        return jsonify({'message': 'Visita eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al eliminar visita: {str(e)}'}), 500

@routes.route('/visitas', methods=['GET', 'OPTIONS'])
def get_visitas():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        # Parámetros opcionales
        all_flag = request.args.get('all', 'false').lower() == 'true'
        supervisor_id_q = request.args.get('supervisor_id', type=int)
        empresa_id_q = request.args.get('empresa_id', type=int)

        user_id = session.get('user_id')
        user = User.query.get(user_id) if user_id else None
        if not user_id and not supervisor_id_q:
            return jsonify({'message': 'No autorizado'}), 401

        # Si el usuario tiene empresa, priorizar filtro por empresa
        empresa = Empresa.query.filter_by(user_id=user_id).first() if user_id else None

        if all_flag and user and user.rol == 'admin':
            visitas = Visita.query.order_by(Visita.fecha.desc()).all()
        elif empresa_id_q:
            visitas = Visita.query.filter_by(empresa_id=empresa_id_q).order_by(Visita.fecha.desc()).all()
        elif empresa:
            visitas = Visita.query.filter_by(empresa_id=empresa.id).order_by(Visita.fecha.desc()).all()
        elif supervisor_id_q:
            visitas = Visita.query.filter_by(supervisor_id=supervisor_id_q).order_by(Visita.fecha.desc()).all()
        else:
            visitas = Visita.query.filter_by(supervisor_id=user_id).order_by(Visita.fecha.desc()).all()
        return jsonify([{
            'id': v.id,
            'fecha': v.fecha.strftime('%Y-%m-%d'),
            'cliente': v.cliente.nombre,
            'supervisor': v.supervisor.nombre,
            'conclusiones': v.conclusiones or ''
        } for v in visitas]), 200
    except Exception as e:
        return jsonify({'message': f'Error al obtener visitas: {str(e)}'}), 500

# CRUD Zonas
# Generar PDF
@routes.route('/generar-pdf/<string:visita_id>', methods=['POST'])
def generar_pdf(visita_id):
    try:
        print(f"DEBUG: Generando PDF para visita {visita_id}", flush=True)
        import sys
        sys.stdout.flush()
        
        # Escribir a archivo para debug
        with open('/tmp/debug_routes.txt', 'a') as f:
            f.write(f"DEBUG: Generando PDF para visita {visita_id}\n")
            f.flush()
        
        # Verificar que la visita existe
        visita = Visita.query.get(visita_id)
        if not visita:
            print(f"DEBUG: Visita {visita_id} no encontrada")
            return jsonify({'message': f'Visita {visita_id} no encontrada'}), 404
        
        print(f"DEBUG: Visita encontrada: {visita.id}", flush=True)
        
        # Usar el nuevo generador HTML
        print(f"DEBUG: Creando generador con upload_folder: {current_app.config['UPLOAD_FOLDER']}", flush=True)
        pdf_generator = HTMLPDFGenerator(upload_folder=current_app.config['UPLOAD_FOLDER'])
        pdf_path = pdf_generator.generar_pdf(visita_id)
        print(f"DEBUG: PDF generado en: {pdf_path}", flush=True)
        
        if not pdf_path:
            print("DEBUG: No se pudo generar PDF")
            return jsonify({'message': 'No se pudo generar PDF'}), 400
        
        # Verificar que el archivo existe
        if not os.path.exists(pdf_path):
            print(f"DEBUG: Archivo PDF no existe en {pdf_path}")
            return jsonify({'message': 'Archivo PDF no encontrado'}), 500
        
        print(f"DEBUG: Enviando archivo PDF: {pdf_path}")
        # Enviar el archivo PDF como respuesta
        return send_file(pdf_path, as_attachment=True, download_name=f'visita-{visita_id}.pdf')
    except Exception as e:
        print(f"DEBUG: Error al generar PDF: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        print(f"FULL TRACEBACK:\n{traceback.format_exc()}", flush=True)
        return jsonify({'message': f'Error al generar PDF: {str(e)}'}), 500

def _enviar_informe_email(visita_id, emails_destino):
    """Función interna para enviar el informe por correo"""
    if isinstance(emails_destino, str):
        emails_destino = [emails_destino]
        
    try:
        print(f"DEBUG: Iniciando _enviar_informe_email para {visita_id} a {emails_destino}", flush=True)
        
        # Verificar que la visita existe
        visita = Visita.query.get(visita_id)
        if not visita:
            raise Exception(f"Visita {visita_id} no encontrada")
        
        # Obtener información de la empresa
        empresa = visita.empresa
        empresa_nombre = empresa.nombre if empresa else 'Empresa'
        
        # Generar el PDF
        pdf_generator = HTMLPDFGenerator(upload_folder=current_app.config['UPLOAD_FOLDER'])
        pdf_path = pdf_generator.generar_pdf(visita_id)
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise Exception("No se pudo generar el PDF")
        
        # Crear el mensaje de correo
        asunto = f"Informe de Visita Técnica - {visita_id} - {visita.cliente.nombre}"
        
        # Renderizar el template HTML
        cuerpo_html = render_template(
            'email_informe.html',
            visita_id=visita_id,
            cliente_nombre=visita.cliente.nombre,
            supervisor_nombre=visita.supervisor.nombre,
            fecha_visita=visita.fecha.strftime('%d/%m/%Y'),
            hora_visita=visita.hora.strftime('%H:%M') if visita.hora else None,
            empresa_nombre=empresa_nombre,
            year=datetime.now().year
        )
        
        # Verificar configuración de correo
        if not current_app.config.get('MAIL_USERNAME'):
            raise Exception("Configuración de correo no encontrada")
        
        # Intentar con SendGrid primero
        if current_app.config.get('USE_SENDGRID') and current_app.config.get('SENDGRID_API_KEY'):
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail as SendGridMail, Attachment, FileContent, FileName, FileType, Disposition
            import base64
            
            sg_mail = SendGridMail(
                from_email=current_app.config.get('MAIL_DEFAULT_SENDER'),
                to_emails=emails_destino,
                subject=asunto,
                html_content=cuerpo_html
            )
            
            with open(pdf_path, 'rb') as f:
                data = f.read()
            encoded_file = base64.b64encode(data).decode()
            
            attached_file = Attachment(
                FileContent(encoded_file),
                FileName(f'informe_visita_{visita_id}.pdf'),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            sg_mail.attachment = attached_file
            
            sg = SendGridAPIClient(current_app.config.get('SENDGRID_API_KEY'))
            sg.send(sg_mail)
        else:
            # Fallback a SMTP tradicional
            for email in emails_destino:
                msg = Message(
                    subject=asunto,
                    recipients=[email],
                    html=cuerpo_html
                )
                with open(pdf_path, 'rb') as pdf_file:
                    msg.attach(
                        filename=f"informe_visita_{visita_id}.pdf",
                        content_type="application/pdf",
                        data=pdf_file.read()
                    )
                mail.send(msg)
        
        return True
    except Exception as e:
        print(f"ERROR en _enviar_informe_email: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        raise

@routes.route('/enviar-informe/<string:visita_id>', methods=['POST', 'OPTIONS'])
def enviar_informe(visita_id):
    """Envía el informe de visita por correo electrónico manualmente"""
    if request.method == 'OPTIONS':
        return ('', 200)
    
    try:
        data = request.json
        email_destino = data.get('email_destino')
        
        if not email_destino:
            return jsonify({'message': 'El correo de destino es requerido'}), 400
        
        _enviar_informe_email(visita_id, email_destino)
        
        return jsonify({
            'message': 'Informe enviado exitosamente',
            'email_destino': email_destino,
            'visita_id': visita_id
        }), 200
        
    except Exception as e:
        print(f"DEBUG: Error al enviar correo: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error al enviar correo: {str(e)}'}), 500

@routes.route('/zonas/<string:visita_id>', methods=['GET'])
def get_zonas(visita_id):
    zonas = Zona.query.filter_by(visita_id=visita_id).all()
    return jsonify([{
        'id': z.id, 'nombre': z.nombre, 'observaciones': z.observaciones, 'actividades': z.actividades,
        'calificacion': z.calificacion, 'foto_url': z.foto_url
    } for z in zonas]), 200

@routes.route('/zonas', methods=['POST'])
def create_zona():
    data = request.json
    zona = Zona(
        visita_id=data['visita_id'], nombre=data['nombre'], observaciones=data['observaciones'],
        actividades=data['actividades'], calificacion=data['calificacion'], foto_url=data.get('foto_url')
    )
    db.session.add(zona)
    db.session.commit()
    return jsonify({'message': 'Zona creada'}), 201

@routes.route('/zonas/<int:id>', methods=['PUT', 'DELETE'])
def manage_zona(id):
    zona = Zona.query.get_or_404(id)
    if request.method == 'PUT':
        data = request.json
        zona.nombre = data['nombre']
        zona.observaciones = data['observaciones']
        zona.actividades = data['actividades']
        zona.calificacion = data['calificacion']
        zona.foto_url = data.get('foto_url')
        db.session.commit()
        return jsonify({'message': 'Zona actualizada'}), 200
    elif request.method == 'DELETE':
        db.session.delete(zona)
        db.session.commit()
        return jsonify({'message': 'Zona eliminada'}), 200

# Endpoint de búsqueda para el centro de atención
@routes.route('/search', methods=['GET'])
def search():
    """Búsqueda avanzada para el centro de atención"""
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')
        
        if not query:
            return jsonify([])
        
        results = []
        
        # Buscar en visitas
        if search_type in ['all', 'visitas']:
            visitas = Visita.query.join(Cliente).join(User).filter(
                or_(
                    Visita.id.ilike(f'%{query}%'),
                    Cliente.nombre.ilike(f'%{query}%'),
                    User.nombre.ilike(f'%{query}%'),
                    Visita.conclusiones.ilike(f'%{query}%')
                )
            ).limit(10).all()
            
            for visita in visitas:
                results.append({
                    'tipo': 'visita',
                    'id': visita.id,
                    'fecha': visita.fecha.strftime('%d/%m/%Y') if visita.fecha else '',
                    'hora': visita.hora.strftime('%H:%M') if visita.hora else '',
                    'cliente_nombre': visita.cliente.nombre if visita.cliente else '',
                    'supervisor_nombre': visita.supervisor.nombre if visita.supervisor else '',
                    'conclusiones': visita.conclusiones[:100] + '...' if visita.conclusiones and len(visita.conclusiones) > 100 else visita.conclusiones or ''
                })
        
        # Buscar en clientes
        if search_type in ['all', 'clientes']:
            clientes = Cliente.query.filter(
                or_(
                    Cliente.nombre.ilike(f'%{query}%'),
                    Cliente.nit.ilike(f'%{query}%'),
                    Cliente.administrador.ilike(f'%{query}%'),
                    Cliente.correo.ilike(f'%{query}%')
                )
            ).limit(10).all()
            
            for cliente in clientes:
                results.append({
                    'tipo': 'cliente',
                    'id': cliente.id,
                    'nombre': cliente.nombre,
                    'nit': cliente.nit,
                    'administrador': cliente.administrador,
                    'correo': cliente.correo,
                    'telefono': cliente.telefono
                })
        
        # Buscar en supervisores (usuarios)
        if search_type in ['all', 'supervisores']:
            supervisores = User.query.filter(
                or_(
                    User.nombre.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%')
                )
            ).limit(10).all()
            
            for supervisor in supervisores:
                results.append({
                    'tipo': 'supervisor',
                    'id': supervisor.id,
                    'nombre': supervisor.nombre,
                    'email': supervisor.email,
                    'rol': supervisor.rol
                })
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error en búsqueda: {e}")
        return jsonify({'error': 'Error en la búsqueda'}), 500

# CRUD Cotizaciones
@routes.route('/cotizaciones', methods=['GET', 'OPTIONS'])
def get_cotizaciones():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': 'No autorizado'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        # Obtener empresa del usuario
        empresa = Empresa.query.filter_by(user_id=user_id).first()
        if not empresa:
            return jsonify({'message': 'No hay empresa asociada al usuario'}), 404
        
        # Filtrar cotizaciones por empresa
        if user.rol == 'admin':
            # Admin puede ver todas las cotizaciones de la empresa
            cotizaciones = Cotizacion.query.filter_by(empresa_id=empresa.id).order_by(Cotizacion.fecha_creacion.desc()).all()
        else:
            # Supervisores solo ven sus propias cotizaciones
            cotizaciones = Cotizacion.query.filter_by(empresa_id=empresa.id, supervisor_id=user_id).order_by(Cotizacion.fecha_creacion.desc()).all()
        
        return jsonify([{
            'id': c.id,
            'fecha_creacion': c.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            'supervisor': c.supervisor.nombre,
            'supervisor_id': c.supervisor_id,
            'estado': c.estado,
            'observaciones': c.observaciones or '',
            'total_items': len(c.items)
        } for c in cotizaciones]), 200
        
    except Exception as e:
        print(f"Error al obtener cotizaciones: {str(e)}")
        return jsonify({'message': f'Error al obtener cotizaciones: {str(e)}'}), 500

@routes.route('/cotizacion/<int:id>', methods=['GET', 'OPTIONS'])
def get_cotizacion(id):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        cotizacion = Cotizacion.query.get_or_404(id)
        
        # Verificar permisos
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        empresa = Empresa.query.filter_by(user_id=user_id).first()
        
        if cotizacion.empresa_id != empresa.id:
            return jsonify({'message': 'No tienes permiso para ver esta cotización'}), 403
        
        if user.rol != 'admin' and cotizacion.supervisor_id != user_id:
            return jsonify({'message': 'No tienes permiso para ver esta cotización'}), 403
        
        return jsonify({
            'id': cotizacion.id,
            'fecha_creacion': cotizacion.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            'supervisor_id': cotizacion.supervisor_id,
            'supervisor': {'nombre': cotizacion.supervisor.nombre, 'email': cotizacion.supervisor.email},
            'empresa': {'nombre': cotizacion.empresa.nombre, 'logo_url': cotizacion.empresa.logo_url},
            'estado': cotizacion.estado,
            'observaciones': cotizacion.observaciones or '',
            'items': [{
                'id': item.id,
                'producto_servicio': item.producto_servicio,
                'cantidad': item.cantidad,
                'uso': item.uso,
                'orden': item.orden
            } for item in sorted(cotizacion.items, key=lambda x: x.orden)]
        }), 200
        
    except Exception as e:
        print(f"Error al obtener cotización: {str(e)}")
        return jsonify({'message': f'Error al obtener cotización: {str(e)}'}), 500

@routes.route('/cotizacion', methods=['POST', 'OPTIONS'])
def create_cotizacion():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': 'No autorizado'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        # Obtener empresa del usuario
        empresa = Empresa.query.filter_by(user_id=user_id).first()
        if not empresa:
            return jsonify({'message': 'No hay empresa asociada al usuario'}), 404
        
        data = request.json
        
        # Validar que haya al menos un item
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'message': 'Debe agregar al menos un producto o servicio'}), 400
        
        # Crear cotización
        cotizacion = Cotizacion(
            fecha_creacion=datetime.utcnow(),
            supervisor_id=user_id,
            empresa_id=empresa.id,
            observaciones=data.get('observaciones', ''),
            estado='pendiente'
        )
        
        db.session.add(cotizacion)
        db.session.flush()
        
        # Agregar items
        for idx, item_data in enumerate(data['items']):
            item = CotizacionItem(
                cotizacion_id=cotizacion.id,
                producto_servicio=item_data['producto_servicio'],
                cantidad=item_data['cantidad'],
                uso=item_data['uso'],
                orden=idx
            )
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify({'message': 'Cotización creada exitosamente', 'id': cotizacion.id}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear cotización: {str(e)}")
        return jsonify({'message': f'Error al crear cotización: {str(e)}'}), 500

@routes.route('/cotizacion/<int:id>', methods=['PUT', 'OPTIONS'])
def update_cotizacion(id):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        cotizacion = Cotizacion.query.get_or_404(id)
        
        # Verificar permisos
        empresa = Empresa.query.filter_by(user_id=user_id).first()
        if cotizacion.empresa_id != empresa.id:
            return jsonify({'message': 'No tienes permiso para editar esta cotización'}), 403
        
        if user.rol != 'admin' and cotizacion.supervisor_id != user_id:
            return jsonify({'message': 'No tienes permiso para editar esta cotización'}), 403
        
        data = request.json
        
        # Validar que haya al menos un item
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'message': 'Debe agregar al menos un producto o servicio'}), 400
        
        # Actualizar cotización
        cotizacion.observaciones = data.get('observaciones', '')
        cotizacion.estado = data.get('estado', cotizacion.estado)
        
        # Eliminar items existentes
        CotizacionItem.query.filter_by(cotizacion_id=id).delete()
        
        # Agregar nuevos items
        for idx, item_data in enumerate(data['items']):
            item = CotizacionItem(
                cotizacion_id=cotizacion.id,
                producto_servicio=item_data['producto_servicio'],
                cantidad=item_data['cantidad'],
                uso=item_data['uso'],
                orden=idx
            )
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify({'message': 'Cotización actualizada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar cotización: {str(e)}")
        return jsonify({'message': f'Error al actualizar cotización: {str(e)}'}), 500

@routes.route('/cotizacion/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_cotizacion(id):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        cotizacion = Cotizacion.query.get_or_404(id)
        
        # Verificar permisos
        empresa = Empresa.query.filter_by(user_id=user_id).first()
        if cotizacion.empresa_id != empresa.id:
            return jsonify({'message': 'No tienes permiso para eliminar esta cotización'}), 403
        
        if user.rol != 'admin' and cotizacion.supervisor_id != user_id:
            return jsonify({'message': 'No tienes permiso para eliminar esta cotización'}), 403
        
        # Eliminar items (cascade debería hacerlo automáticamente)
        db.session.delete(cotizacion)
        db.session.commit()
        
        return jsonify({'message': 'Cotización eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar cotización: {str(e)}")
        return jsonify({'message': f'Error al eliminar cotización: {str(e)}'}), 500

@routes.route('/generar-pdf-cotizacion/<int:id>', methods=['POST', 'OPTIONS'])
def generar_pdf_cotizacion(id):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        from html_cotizacion_generator import HTMLCotizacionGenerator
        
        cotizacion = Cotizacion.query.get_or_404(id)
        
        # Verificar permisos
        user_id = session.get('user_id')
        empresa = Empresa.query.filter_by(user_id=user_id).first()
        if cotizacion.empresa_id != empresa.id:
            return jsonify({'message': 'No tienes permiso para generar el PDF de esta cotización'}), 403
        
        pdf_generator = HTMLCotizacionGenerator(upload_folder=current_app.config['UPLOAD_FOLDER'])
        pdf_path = pdf_generator.generar_pdf(id)
        
        if not pdf_path or not os.path.exists(pdf_path):
            return jsonify({'message': 'No se pudo generar el PDF'}), 500
        
        # Actualizar estado a 'enviada' si estaba en 'pendiente'
        if cotizacion.estado == 'pendiente':
            cotizacion.estado = 'enviada'
            db.session.commit()
        
        return send_file(pdf_path, as_attachment=True, download_name=f'cotizacion-{id}.pdf')
        
    except Exception as e:
        print(f"Error al generar PDF de cotización: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': f'Error al generar PDF: {str(e)}'}), 500

# --- Órdenes de compra ---
@routes.route('/ordenes-compra', methods=['GET', 'OPTIONS'])
def get_ordenes_compra():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': 'No autenticado'}), 401
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404

        empresa = _obtener_empresa_actual(user_id)
        if not empresa:
            return jsonify({'message': 'Debes registrar una empresa antes de gestionar órdenes de compra'}), 400

        query = OrdenCompra.query.filter_by(empresa_id=empresa.id).order_by(OrdenCompra.fecha_creacion.desc())
        if user.rol != 'admin':
            query = query.filter_by(supervisor_id=user_id)

        ordenes = query.all()
        return jsonify([{
            'id': orden.id,
            'numero': orden.numero,
            'fecha_creacion': orden.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            'fecha_entrega': orden.fecha_entrega.strftime('%Y-%m-%d') if orden.fecha_entrega else None,
            'estado': orden.estado,
            'comprador_tipo': orden.comprador_tipo,
            'comprador_nombre': _resolver_nombre_comprador(orden.comprador_tipo, orden.comprador_id),
            'proveedor_nombre': orden.proveedor_nombre,
            'proveedor_nit': orden.proveedor_nit,
            'total_items': len(orden.items),
            'subtotal': orden.subtotal,
            'iva': orden.iva_valor,
            'total': orden.total
        } for orden in ordenes]), 200
    except Exception as e:
        print(f"Error al obtener órdenes de compra: {str(e)}")
        return jsonify({'message': f'Error al obtener órdenes de compra: {str(e)}'}), 500

@routes.route('/orden-compra/<int:id>', methods=['GET', 'OPTIONS'])
def get_orden_compra(id):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': 'No autenticado'}), 401
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404

        orden = OrdenCompra.query.get_or_404(id)
        empresa = _obtener_empresa_actual(user_id)
        if not empresa or orden.empresa_id != empresa.id:
            return jsonify({'message': 'No tienes permiso para ver esta orden'}), 403

        if user.rol != 'admin' and orden.supervisor_id != user_id:
            return jsonify({'message': 'No tienes permiso para ver esta orden'}), 403

        return jsonify({
            'id': orden.id,
            'numero': orden.numero,
            'fecha_creacion': orden.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            'fecha_entrega': orden.fecha_entrega.strftime('%Y-%m-%d') if orden.fecha_entrega else None,
            'comprador_tipo': orden.comprador_tipo,
            'comprador_id': orden.comprador_id,
            'comprador_nombre': _resolver_nombre_comprador(orden.comprador_tipo, orden.comprador_id),
            'proveedor_nombre': orden.proveedor_nombre,
            'proveedor_nit': orden.proveedor_nit,
            'proveedor_direccion': orden.proveedor_direccion,
            'proveedor_tipo_insumos': orden.proveedor_tipo_insumos,
            'condiciones_pago': orden.condiciones_pago,
            'notas': orden.notas,
            'estado': orden.estado,
            'subtotal': orden.subtotal,
            'iva': orden.iva_valor,
            'total': orden.total,
            'proveedor_id': orden.proveedor_id,
            'items': [{
                'id': item.id,
                'descripcion': item.descripcion,
                'cantidad': item.cantidad,
                'unidad': item.unidad,
                'precio_unitario': item.precio_unitario,
                'comentarios': item.comentarios,
                'posicion': item.posicion,
                'subtotal': _calcular_total_estimado([item])
            } for item in sorted(orden.items, key=lambda x: x.posicion)]
        }), 200
    except Exception as e:
        print(f"Error al obtener orden de compra: {str(e)}")
        return jsonify({'message': f'Error al obtener orden de compra: {str(e)}'}), 500

@routes.route('/orden-compra', methods=['POST', 'OPTIONS'])
def create_orden_compra():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': 'No autenticado'}), 401
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404

        empresa = _obtener_empresa_actual(user_id)
        if not empresa:
            return jsonify({'message': 'Debes registrar una empresa antes de crear órdenes de compra'}), 400

        data = request.json or {}
        items = data.get('items', [])
        if not isinstance(items, list) or len(items) == 0:
            return jsonify({'message': 'Debes agregar al menos un item a la orden'}), 400

        comprador_tipo = data.get('comprador_tipo')
        comprador_id = data.get('comprador_id')
        if comprador_tipo not in ['cliente', 'empresa']:
            return jsonify({'message': 'Tipo de comprador inválido'}), 400
        if not comprador_id:
            return jsonify({'message': 'El comprador es requerido'}), 400

        proveedor_id = data.get('proveedor_id')
        proveedor = None
        if proveedor_id:
            proveedor = Proveedor.query.get(proveedor_id)
            if not proveedor:
                return jsonify({'message': 'Proveedor no encontrado'}), 404

        orden = OrdenCompra(
            numero=data.get('numero') or _generar_consecutivo_orden(),
            fecha_creacion=datetime.utcnow(),
            fecha_entrega=datetime.strptime(data['fecha_entrega'], '%Y-%m-%d').date() if data.get('fecha_entrega') else None,
            comprador_tipo=comprador_tipo,
            comprador_id=int(comprador_id),
            proveedor_id=proveedor.id if proveedor else None,
            proveedor_nombre=data.get('proveedor_nombre', proveedor.nombre_comercial if proveedor else '').strip(),
            proveedor_nit=data.get('proveedor_nit', proveedor.nit if proveedor else '').strip(),
            proveedor_direccion=data.get('proveedor_direccion', proveedor.direccion if proveedor else '').strip(),
            proveedor_tipo_insumos=data.get('proveedor_tipo_insumos', proveedor.tipo_insumos if proveedor else '').strip(),
            condiciones_pago=data.get('condiciones_pago', '').strip(),
            notas=data.get('notas', '').strip(),
            estado=data.get('estado', 'borrador'),
            empresa_id=empresa.id,
            supervisor_id=user_id
        )

        if not orden.proveedor_nombre:
            return jsonify({'message': 'El proveedor es requerido'}), 400

        db.session.add(orden)
        db.session.flush()

        for index, item in enumerate(items):
            if not item.get('descripcion') or not item.get('cantidad') or not item.get('unidad'):
                db.session.rollback()
                return jsonify({'message': 'Todos los items deben tener descripción, cantidad y unidad'}), 400
            item_model = OrdenCompraItem(
                orden_id=orden.id,
                descripcion=item['descripcion'],
                cantidad=item['cantidad'],
                unidad=item['unidad'],
                precio_unitario=_parse_float(item.get('precio_unitario')),
                comentarios=item.get('comentarios', ''),
                posicion=index
            )
            db.session.add(item_model)

        subtotal, iva_valor, total = _calcular_totales(data, items)
        orden.subtotal = subtotal
        orden.iva_valor = iva_valor
        orden.total = total

        db.session.commit()
        return jsonify({'message': 'Orden de compra creada exitosamente', 'id': orden.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear orden de compra: {str(e)}")
        return jsonify({'message': f'Error al crear orden de compra: {str(e)}'}), 500

@routes.route('/orden-compra/<int:id>', methods=['PUT', 'OPTIONS'])
def update_orden_compra(id):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': 'No autenticado'}), 401
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404

        orden = OrdenCompra.query.get_or_404(id)
        empresa = _obtener_empresa_actual(user_id)
        if not empresa or orden.empresa_id != empresa.id:
            return jsonify({'message': 'No tienes permiso para editar esta orden'}), 403
        if user.rol != 'admin' and orden.supervisor_id != user_id:
            return jsonify({'message': 'No tienes permiso para editar esta orden'}), 403

        data = request.json or {}
        items = data.get('items', [])
        if not isinstance(items, list) or len(items) == 0:
            return jsonify({'message': 'Debes agregar al menos un item a la orden'}), 400

        comprador_tipo = data.get('comprador_tipo')
        comprador_id = data.get('comprador_id')
        if comprador_tipo not in ['cliente', 'empresa']:
            return jsonify({'message': 'Tipo de comprador inválido'}), 400
        if not comprador_id:
            return jsonify({'message': 'El comprador es requerido'}), 400

        proveedor_id = data.get('proveedor_id')
        proveedor = None
        if proveedor_id:
            proveedor = Proveedor.query.get(proveedor_id)
            if not proveedor:
                return jsonify({'message': 'Proveedor no encontrado'}), 404

        orden.fecha_entrega = datetime.strptime(data['fecha_entrega'], '%Y-%m-%d').date() if data.get('fecha_entrega') else None
        orden.comprador_tipo = comprador_tipo
        orden.comprador_id = int(comprador_id)
        orden.proveedor_id = proveedor.id if proveedor else None
        orden.proveedor_nombre = data.get('proveedor_nombre', proveedor.nombre_comercial if proveedor else '').strip()
        orden.proveedor_nit = data.get('proveedor_nit', proveedor.nit if proveedor else '').strip()
        orden.proveedor_direccion = data.get('proveedor_direccion', proveedor.direccion if proveedor else '').strip()
        orden.proveedor_tipo_insumos = data.get('proveedor_tipo_insumos', proveedor.tipo_insumos if proveedor else '').strip()
        orden.condiciones_pago = data.get('condiciones_pago', '').strip()
        orden.notas = data.get('notas', '').strip()
        orden.estado = data.get('estado', orden.estado)

        if not orden.proveedor_nombre:
            return jsonify({'message': 'El proveedor es requerido'}), 400

        OrdenCompraItem.query.filter_by(orden_id=id).delete()

        for index, item in enumerate(items):
            if not item.get('descripcion') or not item.get('cantidad') or not item.get('unidad'):
                db.session.rollback()
                return jsonify({'message': 'Todos los items deben tener descripción, cantidad y unidad'}), 400
            item_model = OrdenCompraItem(
                orden_id=orden.id,
                descripcion=item['descripcion'],
                cantidad=item['cantidad'],
                unidad=item['unidad'],
                precio_unitario=_parse_float(item.get('precio_unitario')),
                comentarios=item.get('comentarios', ''),
                posicion=index
            )
            db.session.add(item_model)

        subtotal, iva_valor, total = _calcular_totales(data, items)
        orden.subtotal = subtotal
        orden.iva_valor = iva_valor
        orden.total = total

        db.session.commit()
        return jsonify({'message': 'Orden de compra actualizada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar orden de compra: {str(e)}")
        return jsonify({'message': f'Error al actualizar orden de compra: {str(e)}'}), 500

@routes.route('/orden-compra/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_orden_compra(id):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': 'No autenticado'}), 401
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404

        orden = OrdenCompra.query.get_or_404(id)
        empresa = _obtener_empresa_actual(user_id)
        if not empresa or orden.empresa_id != empresa.id:
            return jsonify({'message': 'No tienes permiso para eliminar esta orden'}), 403
        if user.rol != 'admin' and orden.supervisor_id != user_id:
            return jsonify({'message': 'No tienes permiso para eliminar esta orden'}), 403

        OrdenCompraItem.query.filter_by(orden_id=id).delete()
        db.session.delete(orden)
        db.session.commit()
        return jsonify({'message': 'Orden de compra eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar orden de compra: {str(e)}")
        return jsonify({'message': f'Error al eliminar orden de compra: {str(e)}'}), 500

@routes.route('/generar-pdf-orden/<int:id>', methods=['POST', 'OPTIONS'])
def generar_pdf_orden(id):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'message': 'No autenticado'}), 401
        orden = OrdenCompra.query.get_or_404(id)
        empresa = _obtener_empresa_actual(user_id)
        if not empresa or orden.empresa_id != empresa.id:
            return jsonify({'message': 'No tienes permiso para generar el PDF de esta orden'}), 403

        generator = HTMLOrdenGenerator(upload_folder=current_app.config['UPLOAD_FOLDER'])
        pdf_path = generator.generar_pdf(id)
        if not pdf_path or not os.path.exists(pdf_path):
            return jsonify({'message': 'No se pudo generar el PDF'}), 500
        return send_file(pdf_path, as_attachment=True, download_name=f'orden-compra-{orden.numero}.pdf')
    except Exception as e:
        print(f"Error al generar PDF de orden: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': f'Error al generar PDF de orden: {str(e)}'}), 500