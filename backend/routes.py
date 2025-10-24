from pdf_generator import generate_pdf
from flask_mail import Mail, Message
from flask import Blueprint, request, jsonify, session, send_from_directory, current_app
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

@routes.before_request
def log_request_info():
    print(f"REQUEST: {request.method} {request.path}")
    print(f"HEADERS: {dict(request.headers)}")
    print(f"CONTENT_TYPE: {request.content_type}")
    if request.is_json:
        print(f"JSON_DATA: {request.get_json()}")
    else:
        print(f"FORM_DATA: {request.form}")
        print(f"RAW_DATA: {request.get_data()}")

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
        print("=== DEBUG: Starting create_usuario ===")
        print(f"DEBUG: Method: {request.method}")
        print(f"DEBUG: Headers: {dict(request.headers)}")
        print(f"DEBUG: Content-Type: {request.content_type}")
        print(f"DEBUG: Is JSON: {request.is_json}")
        
        # Intentar obtener datos de diferentes formas
        if request.is_json:
            data = request.get_json()
            print(f"DEBUG: JSON data: {data}")
        else:
            print("DEBUG: Not JSON, trying form data")
            data = request.form.to_dict()
            print(f"DEBUG: Form data: {data}")
        
        if not data:
            print("DEBUG: No data received")
            return jsonify({'message': 'No se recibieron datos'}), 400
        
        # Validar campos requeridos
        required_fields = ['nombre', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                print(f"DEBUG: Missing field: {field}")
                return jsonify({'message': f'El campo {field} es requerido'}), 400
        
        # Verificar si el email ya existe
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            print(f"DEBUG: Email exists: {data['email']}")
            return jsonify({'message': 'El email ya está registrado'}), 400
        
        # Crear usuario
        user = User(nombre=data['nombre'], email=data['email'], rol=data.get('rol', 'user'))
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        print(f"DEBUG: User created: {user.id}")
        
        # Iniciar sesión
        session['user_id'] = user.id
        session['rol'] = user.rol
        
        return jsonify({
            'message': 'Usuario creado y sesión iniciada',
            'rol': user.rol,
            'nombre': user.nombre
        }), 201
        
    except Exception as e:
        print(f"DEBUG: Exception: {str(e)}")
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'message': f'Error: {str(e)}'}), 500

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
@routes.route('/visitas', methods=['GET'])
def get_visitas():
    user_id = session.get('user_id')
    rol = session.get('rol')
    if rol == 'admin':
        visitas = Visita.query.all()
    else:
        visitas = Visita.query.filter((Visita.supervisor_id == user_id) | (Visita.tecnico_id == user_id)).all()
    return jsonify([{
        'id': v.id, 'fecha': v.fecha.isoformat(), 'supervisor': v.supervisor.nombre, 'tecnico': v.tecnico.nombre,
        'cliente': v.cliente.nombre, 'goal': v.goal, 'calificacion': v.calificacion
    } for v in visitas]), 200

@routes.route('/visitas', methods=['POST'])
def create_visita():
    data = request.json
    # Generar ID: contador por tipo + tipo + fecha
    tipo = data['tipo_codigo']
    fecha_str = data['fecha'].replace('-', '')
    count = Visita.query.filter(Visita.id.like(f'%-{tipo}-{fecha_str}')).count() + 1
    visita_id = f"{count}-{tipo}-{fecha_str}"
    visita = Visita(
        id=visita_id, fecha=datetime.fromisoformat(data['fecha']), supervisor_id=data['supervisor_id'],
        tecnico_id=data['tecnico_id'], cliente_id=data['cliente_id'], goal=data['goal'], calificacion=data['calificacion'],
        notas=data.get('notas'), seguridad_obs=data.get('seguridad_obs'), productividad_obs=data.get('productividad_obs'),
        conclusiones_obs=data.get('conclusiones_obs')
    )
    db.session.add(visita)
    db.session.commit()
    return jsonify({'message': 'Visita creada', 'id': visita_id}), 201

@routes.route('/visitas/<string:id>', methods=['PUT', 'DELETE'])
def manage_visita(id):
    visita = Visita.query.get_or_404(id)
    if request.method == 'PUT':
        data = request.json
        visita.fecha = datetime.fromisoformat(data['fecha'])
        visita.supervisor_id = data['supervisor_id']
        visita.tecnico_id = data['tecnico_id']
        visita.cliente_id = data['cliente_id']
        visita.goal = data['goal']
        visita.calificacion = data['calificacion']
        visita.notas = data.get('notas')
        visita.seguridad_obs = data.get('seguridad_obs')
        visita.productividad_obs = data.get('productividad_obs')
        visita.conclusiones_obs = data.get('conclusiones_obs')
        db.session.commit()
        return jsonify({'message': 'Visita actualizada'}), 200
    elif request.method == 'DELETE':
        db.session.delete(visita)
        db.session.commit()
        return jsonify({'message': 'Visita eliminada'}), 200

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
# CRUD Zonas
# Generar PDF
@routes.route('/generar-pdf/<string:visita_id>', methods=['POST'])
def generar_pdf(visita_id):
    pdf_path = generate_pdf(visita_id)
    if not pdf_path:
        return jsonify({'message': 'No se puede generar PDF: falta al menos una foto'}), 400
    data = request.json or {}
    if data.get('enviar_email'):
        visita = Visita.query.get(visita_id)
        msg = Message('Informe de Visita Técnica', recipients=[visita.cliente.correo])
        msg.body = 'Adjunto el informe de la visita técnica.'
        with open(pdf_path, 'rb') as f:
            msg.attach(pdf_path, 'application/pdf', f.read())
        current_app.extensions['mail'].send(msg)
    return jsonify({'url': f'/static/{pdf_path}'}), 200
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