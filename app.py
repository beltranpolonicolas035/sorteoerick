import os
from flask import Flask
from dotenv import load_dotenv

# 1. Cargar variables de entorno
load_dotenv()

# 2. Creamos la app
app = Flask(__name__, template_folder='template')

# 3. Configuraciones
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('Zona B&R Rifa', os.getenv('MAIL_USERNAME'))

# Configuración de archivos
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 4. Inicializamos extensiones (Importamos aquí para evitar el ciclo)
from base_datos import db
from extensiones import mail

db.init_app(app)
mail.init_app(app)

# 5. REGISTRO DE BLUEPRINTS
from rutas.publico import publico_bp
from rutas.admin import admin_bp
from rutas.ingreso import ingreso_bp

app.register_blueprint(publico_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(ingreso_bp)

# 6. Crear tablas
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)