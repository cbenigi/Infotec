import os
from dotenv import load_dotenv
from flask_mail import Mail
from routes import routes, mail as routes_mail
from flask import Flask
from flask_cors import CORS
from models import db
from config import config

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)

# Configurar según el entorno
config_name = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

# Asegurar carpeta de uploads
os.makedirs(app.config.get('UPLOAD_FOLDER', '/app/uploads'), exist_ok=True)

# Registrar blueprint
app.register_blueprint(routes)

# Configurar CORS
cors_origins = app.config.get('CORS_ORIGINS', '*')
if isinstance(cors_origins, str) and cors_origins != '*':
    cors_origins = [origin.strip() for origin in cors_origins.split(',')]

print(f"🔧 CORS Origins configurados: {cors_origins}")

CORS(app, 
     supports_credentials=True, 
     origins=cors_origins,
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Cookies de sesión
if app.config.get('DEBUG') or os.environ.get('FLASK_ENV') == 'development':
    # Entorno de desarrollo (Local): Secure=False para soportar HTTP (necesario para acceso desde IP/móvil)
    app.config.update(
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=False,
    )
    print("🍪 Cookies configuradas para DESARROLLO (Secure=False, SameSite=Lax)")
else:
    # Entorno de producción (Deploy): Secure=True y SameSite=None para soportar cross-site
    app.config.update(
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_SECURE=True,
    )
    print("🍪 Cookies configuradas para PRODUCCIÓN (Secure=True, SameSite=None)")

# Inicializar base de datos
db.init_app(app)

# Inicializar mail desde routes
routes_mail.init_app(app)

print(f"📧 Configuración de correo:")
print(f"   - Servidor: {app.config.get('MAIL_SERVER', 'No configurado')}")
print(f"   - Puerto: {app.config.get('MAIL_PORT', 'No configurado')}")
print(f"   - Usuario: {app.config.get('MAIL_USERNAME', 'No configurado')}")
print(f"   - TLS: {app.config.get('MAIL_USE_TLS', False)}")

# Crear tablas
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])