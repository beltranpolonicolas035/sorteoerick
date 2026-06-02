from flask_sqlalchemy import SQLAlchemy
import os

# Inicializamos la instancia de la base de datos con engine_options
# pool_pre_ping=True verifica que la conexión esté viva antes de usarla
# pool_recycle=280 fuerza a renovar la conexión cada pocos minutos
db = SQLAlchemy(engine_options={
    "pool_pre_ping": True,
    "pool_recycle": 280
})

# Función para configurar la base de datos
def configurar_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    db.init_app(app)