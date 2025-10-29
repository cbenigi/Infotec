import os
from flask_mail import Mail
from routes import routes
from flask import Flask
from flask_cors import CORS
from models import db
from config import config

app = Flask(__name__)

# Configurar según el entorno
config_name = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

# Registrar blueprint
app.register_blueprint(routes)

# Configurar CORS
CORS(app, supports_credentials=True, origins=app.config['CORS_ORIGINS'])

# Inicializar base de datos
db.init_app(app)

# Inicializar mail
mail = Mail()
mail.init_app(app)

# Crear tablas
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])