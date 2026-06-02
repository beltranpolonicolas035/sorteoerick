from flask_sqlalchemy import SQLAlchemy
import os

# Inicializamos la instancia de la base de datos
db = SQLAlchemy()

# Función para configurar la base de datos sin importar 'app' directamente
def configurar_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    db.init_app(app)