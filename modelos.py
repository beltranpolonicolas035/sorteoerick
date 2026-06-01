from base_datos import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Compra(db.Model):
    __tablename__ = 'compras'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.BigInteger, nullable=False)
    whatsapp = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(50), nullable=False)
    cantidad_tickets = db.Column(db.Integer, nullable=False, default=20) 
    comprobante_pago = db.Column(db.String(200), nullable=False) 
    estado = db.Column(db.String(20), default='pendiente')
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    boletas = db.relationship('Boleta', backref='compra', lazy=True)

class Boleta(db.Model):
    __tablename__ = 'boletas'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)
    estado = db.Column(db.String(20), default='disponible')
    compra_id = db.Column(db.Integer, db.ForeignKey('compras.id'), nullable=True)

class Ganador(db.Model):
    __tablename__ = 'ganador_oficial'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.String(5), nullable=False)
    premio = db.Column(db.String(100), nullable=False)
    fecha_publicacion = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())