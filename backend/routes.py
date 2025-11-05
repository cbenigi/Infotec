from html_pdf_generator import HTMLPDFGenerator
from flask_mail import Mail, Message
from flask import Blueprint, request, jsonify, session, send_from_directory, current_app, send_file
import os
from werkzeug.utils import secure_filename
from models import db, User, Empresa, Cliente, Visita, Zona, Cotizacion, CotizacionItem
from sqlalchemy import or_
from werkzeug.security import check_password_hash
from datetime import datetime
import traceback

routes = Blueprint('routes', __name__)

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
        user = User(nombre=data['nombre'], email=data['email'], rol=data.get('rol', 'user'))
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
        'id': empresa.id,
        'nombre': empresa.nombre,
        'nit': empresa.nit,
        'telefono': empresa.telefono,
        'correo': empresa.correo,
        'direccion': empresa.direccion,
        'logo_url': empresa.logo_url
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

# CRUD Clientes
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