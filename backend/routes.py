from pdf_generator import generate_pdf
from flask_mail import Mail, Message
from flask import Blueprint, request, jsonify, session, send_from_directory, current_app, send_file
import os
from werkzeug.utils import secure_filename
from models import db, User, Empresa, Cliente, Visita, Zona
from werkzeug.security import check_password_hash
from datetime import datetime
import traceback

routes = Blueprint('routes', __name__)

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
@routes.route('/login', methods=['POST'])
def login():
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
@routes.route('/empresa', methods=['GET'])
def get_empresa():
    user_id = session.get('user_id')
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

@routes.route('/empresa', methods=['POST'])
def create_empresa():
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

@routes.route('/empresa', methods=['PUT'])
def update_empresa():
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
    clientes = Cliente.query.all()
    return jsonify([{'id': c.id, 'nit': c.nit, 'nombre': c.nombre, 'administrador': c.administrador, 'correo': c.correo, 'tipo_codigo': c.tipo_codigo} for c in clientes]), 200

@routes.route('/clientes', methods=['POST'])
def create_cliente():
    data = request.json
    cliente = Cliente(nit=data['nit'], nombre=data['nombre'], administrador=data['administrador'], correo=data['correo'], tipo_codigo=data['tipo_codigo'])
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
        db.session.commit()
        return jsonify({'message': 'Cliente actualizado'}), 200
    elif request.method == 'DELETE':
        db.session.delete(cliente)
        db.session.commit()
        return jsonify({'message': 'Cliente eliminado'}), 200

# CRUD Visitas



# Upload de imágenes
@routes.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
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
        # Generar ID automático
        fecha = datetime.strptime(data['fecha'], '%Y-%m-%d')
        visita_id = f"{fecha.strftime('%d%m%Y')}-{data.get('tipo_codigo', 'AL')}-{datetime.now().strftime('%H%M')}"
        
        visita = Visita(
            id=visita_id,
            fecha=fecha,
            supervisor_id=data['supervisor_id'],
            cliente_id=data['cliente_id'],
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
        visita.supervisor_id = data['supervisor_id']
        visita.cliente_id = data['cliente_id']
        visita.conclusiones = data.get('conclusiones', '')
        
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

@routes.route('/visitas', methods=['GET'])
def get_visitas():
    try:
        visitas = Visita.query.all()
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
        print(f"DEBUG: Generando PDF para visita {visita_id}")
        
        # Verificar que la visita existe
        visita = Visita.query.get(visita_id)
        if not visita:
            print(f"DEBUG: Visita {visita_id} no encontrada")
            return jsonify({'message': f'Visita {visita_id} no encontrada'}), 404
        
        print(f"DEBUG: Visita encontrada: {visita.id}")
        
        pdf_path = generate_pdf(visita_id)
        print(f"DEBUG: PDF generado en: {pdf_path}")
        
        if not pdf_path:
            print("DEBUG: No se pudo generar PDF - falta al menos una foto")
            return jsonify({'message': 'No se puede generar PDF: falta al menos una foto'}), 400
        
        # Verificar que el archivo existe
        if not os.path.exists(pdf_path):
            print(f"DEBUG: Archivo PDF no existe en {pdf_path}")
            return jsonify({'message': 'Archivo PDF no encontrado'}), 500
        
        print(f"DEBUG: Enviando archivo PDF: {pdf_path}")
        # Enviar el archivo PDF como respuesta
        return send_file(pdf_path, as_attachment=True, download_name=f'visita-{visita_id}.pdf')
    except Exception as e:
        print(f"DEBUG: Error al generar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
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