from flask_mail import Mail
from routes import routes
from flask import Flask
from flask_cors import CORS
from models import db
from config import Config

app = Flask(__name__)
app.register_blueprint(routes)
app.config.from_object(Config)
CORS(app, supports_credentials=True)
db.init_app(app)
mail = Mail()
mail.init_app(app)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)