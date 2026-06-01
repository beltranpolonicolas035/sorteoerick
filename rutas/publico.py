import os
import time
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from base_datos import db
from modelos import Compra, Boleta, Ganador

publico_bp = Blueprint('publico', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@publico_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombre_cliente = request.form.get('nombre')
        cedula_cliente = request.form.get('cedula')
        whatsapp_cliente = request.form.get('whatsapp')
        correo_cliente = request.form.get('correo')
        ciudad_cliente = request.form.get('ciudad')
        
        cantidad_solicitada = request.form.get('ticketQuantity')
        cantidad_final = int(cantidad_solicitada) if cantidad_solicitada else 20
        
        if cantidad_final > 99999:
            cantidad_final = 99999

        if 'comprobante' not in request.files:
            return "Error: No se seleccionó ningún archivo de comprobante.", 400
            
        file = request.files['comprobante']
        
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp_unico = int(time.time())
            filename_final = f"{timestamp_unico}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename_final))
            
            nueva_compra = Compra(
                nombre=nombre_cliente,
                cedula=int(cedula_cliente),
                whatsapp=whatsapp_cliente,
                correo=correo_cliente,
                ciudad=ciudad_cliente,
                cantidad_tickets=cantidad_final, 
                comprobante_pago=filename_final,  
                estado='pendiente'
            )
            db.session.add(nueva_compra)
            db.session.commit()
            
            flash("¡Envío Exitoso! Tu comprobante ha sido recibido.")
            return redirect(url_for('publico.index'))
        else:
            return "Error: Formato no permitido o archivo inválido.", 400

    # Lógica de carga para GET
    tickets_vendidos = Boleta.query.filter_by(estado='vendido').count()
    porcentaje_final = round((tickets_vendidos / 100000) * 100, 1)
    ganador_actual = Ganador.query.first()

    return render_template('index.html', tickets_vendidos=tickets_vendidos, porcentaje=porcentaje_final, ganador=ganador_actual)