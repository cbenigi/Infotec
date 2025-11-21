from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Roles funcionales: 'admin', 'aseo', 'nomina'
    rol = db.Column(db.String(10), nullable=False, default='aseo')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Empresa(db.Model):
    __tablename__ = 'empresas'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
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
    logo_url = db.Column(db.String(200))  # URL relativa al logo del cliente

class Visita(db.Model):
    __tablename__ = 'visitas'
    id = db.Column(db.String(20), primary_key=True)  # Autogenerado: NUM-TIPO-FECHA
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=True)  # Campo de hora opcional
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'))
    conclusiones = db.Column(db.Text)

    supervisor = db.relationship('User', foreign_keys=[supervisor_id])
    cliente = db.relationship('Cliente')
    empresa = db.relationship('Empresa')
    zonas = db.relationship('Zona', backref='visita', lazy=True)

class Zona(db.Model):
    __tablename__ = 'zonas'
    id = db.Column(db.Integer, primary_key=True)
    visita_id = db.Column(db.String(20), db.ForeignKey('visitas.id'), nullable=False)
    seccion = db.Column(db.String(50), nullable=False)  # 'Aseo y Limpieza', 'Seguridad y Salud', 'Colaborador'
    concepto_actividad = db.Column(db.String(100), nullable=False)
    calificacion = db.Column(Enum('Buena', 'Media', 'Mala', name='calif_enum'), nullable=False)
    observaciones = db.Column(db.Text)
    foto_url = db.Column(db.String(200))  # URL relativa a la imagen subida (solo para Aseo y Seguridad)

class Cotizacion(db.Model):
    __tablename__ = 'cotizaciones'
    id = db.Column(db.Integer, primary_key=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    observaciones = db.Column(db.Text)
    estado = db.Column(db.String(20), nullable=False, default='pendiente')  # pendiente, enviada, aprobada, rechazada
    
    supervisor = db.relationship('User', foreign_keys=[supervisor_id])
    empresa = db.relationship('Empresa')
    items = db.relationship('CotizacionItem', backref='cotizacion', lazy=True, cascade='all, delete-orphan')

class CotizacionItem(db.Model):
    __tablename__ = 'cotizacion_items'
    id = db.Column(db.Integer, primary_key=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey('cotizaciones.id'), nullable=False)
    producto_servicio = db.Column(db.String(200), nullable=False)
    cantidad = db.Column(db.String(50), nullable=False)
    uso = db.Column(db.String(200), nullable=False)
    orden = db.Column(db.Integer, nullable=False, default=0)

class OrdenCompra(db.Model):
    __tablename__ = 'ordenes_compra'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(30), unique=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False)
    fecha_entrega = db.Column(db.Date, nullable=True)
    comprador_tipo = db.Column(db.String(20), nullable=False, default='cliente')
    comprador_id = db.Column(db.Integer, nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=True)
    proveedor_nombre = db.Column(db.String(150), nullable=False)
    proveedor_nit = db.Column(db.String(50))
    proveedor_direccion = db.Column(db.String(200))
    proveedor_tipo_insumos = db.Column(db.String(200))
    condiciones_pago = db.Column(db.String(200))
    notas = db.Column(db.Text)
    estado = db.Column(db.String(20), nullable=False, default='borrador')
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subtotal = db.Column(db.Float, nullable=True)
    iva_valor = db.Column(db.Float, nullable=True)
    total = db.Column(db.Float, nullable=True)

    empresa = db.relationship('Empresa')
    supervisor = db.relationship('User', foreign_keys=[supervisor_id])
    proveedor = db.relationship('Proveedor')
    items = db.relationship('OrdenCompraItem', backref='orden_compra', lazy=True, cascade='all, delete-orphan')

class OrdenCompraItem(db.Model):
    __tablename__ = 'orden_compra_items'
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('ordenes_compra.id'), nullable=False)
    descripcion = db.Column(db.String(250), nullable=False)
    cantidad = db.Column(db.String(50), nullable=False)
    unidad = db.Column(db.String(30), nullable=False)
    precio_unitario = db.Column(db.Float, nullable=True)
    comentarios = db.Column(db.String(250))
    posicion = db.Column(db.Integer, nullable=False, default=0)

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre_comercial = db.Column(db.String(150), nullable=False)
    nit = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(200))
    tipo_insumos = db.Column(db.String(200))

class EmpresaAcceso(db.Model):
    __tablename__ = 'empresa_accesos'
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    solicitante_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='pendiente')  # pendiente, aprobado, rechazado
    mensaje = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    empresa = db.relationship('Empresa')
    solicitante = db.relationship('User', foreign_keys=[solicitante_id])

class EmpresaNominaRelacion(db.Model):
    __tablename__ = 'empresa_nomina_relaciones'
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('empresa_id', 'user_id', name='uq_nomina_empresa_user'),
    )

    empresa = db.relationship('Empresa')
    user = db.relationship('User')