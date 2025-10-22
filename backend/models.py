from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(10), nullable=False, default='user')  # 'admin' or 'user'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Empresa(db.Model):
    __tablename__ = 'empresas'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    nit = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(120), nullable=False)
    direccion = db.Column(db.String(200))
    logo_url = db.Column(db.String(200))  # URL relativa al logo subido
    
    user = db.relationship('User', backref='empresa')

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nit = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    administrador = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), nullable=False)
    tipo_codigo = db.Column(db.String(10), nullable=False)  # e.g., 'AL'

class Visita(db.Model):
    __tablename__ = 'visitas'
    id = db.Column(db.String(20), primary_key=True)  # Autogenerado: NUM-TIPO-FECHA
    fecha = db.Column(db.Date, nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    goal = db.Column(db.Integer, nullable=False)
    calificacion = db.Column(db.Integer, nullable=False)
    notas = db.Column(db.Text)
    seguridad_obs = db.Column(db.Text)
    productividad_obs = db.Column(db.Text)
    conclusiones_obs = db.Column(db.Text)

    supervisor = db.relationship('User', foreign_keys=[supervisor_id])
    tecnico = db.relationship('User', foreign_keys=[tecnico_id])
    cliente = db.relationship('Cliente')
    zonas = db.relationship('Zona', backref='visita', lazy=True)

class Zona(db.Model):
    __tablename__ = 'zonas'
    id = db.Column(db.Integer, primary_key=True)
    visita_id = db.Column(db.String(20), db.ForeignKey('visitas.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    observaciones = db.Column(db.Text, nullable=False)
    actividades = db.Column(db.Text, nullable=False)
    calificacion = db.Column(Enum('Bueno', 'Regular', 'Malo', name='calif_enum'), nullable=False)
    foto_url = db.Column(db.String(200))  # URL relativa a la imagen subida