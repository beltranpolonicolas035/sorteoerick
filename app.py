import os
from flask import Flask
from dotenv import load_dotenv

# 1. Cargar variables de entorno (solo funciona localmente)
load_dotenv()

# 2. Creamos la app
app = Flask(__name__, template_folder='template')

# 3. Configuraciones
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- CONFIGURACIÓN DE CORREO OPTIMIZADA ---
# Usamos os.environ.get para leer directamente de Render
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('Zona B&R Rifa', os.environ.get('MAIL_USERNAME'))

# Configuración de archivos
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 4. Inicializamos extensiones
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
    # debug=False es mejor para producción, aunque en Render 
    # esto no afecta tanto al ser manejado por Gunicorn
    app.run(debug=False)