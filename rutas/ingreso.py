import os
from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from werkzeug.utils import secure_filename
from modelos import Usuario

# --- CONFIGURACIÓN DE SEGURIDAD PARA ARCHIVOS ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

ingreso_bp = Blueprint('ingreso', __name__)

@ingreso_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        usuario_encontrado = Usuario.query.filter_by(username=username).first()
        
        # Validación con sesión
        if usuario_encontrado and usuario_encontrado.password == password:
            session.permanent = True
            session['admin_logeado'] = True
            return redirect(url_for('admin.admin'))
        else:
            error = 'Usuario o contraseña incorrectos.'
            
    return render_template('login.html', error=error)

@ingreso_bp.route('/logout')
def logout():
    session.pop('admin_logeado', None)
    return redirect(url_for('publico.index'))

# --- EJEMPLO DE CÓMO USAR LA VALIDACIÓN EN TU RUTA DE COMPRA ---
# Nota: Esta ruta es un ejemplo, adáptala a donde esté tu formulario de subida
@ingreso_bp.route('/subir-pago', methods=['POST'])
def subir_pago():
    if 'archivo' not in request.files:
        flash('No se envió ningún archivo', 'danger')
        return redirect(request.url)
    
    file = request.files['archivo']
    
    if file.filename == '':
        flash('Selecciona un archivo válido', 'danger')
        return redirect(request.url)
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Guardar en la carpeta configurada en app.py
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        flash('Archivo subido correctamente', 'success')
        return redirect(url_for('publico.index'))
    else:
        flash('Formato no permitido. Solo se aceptan: PNG, JPG, JPEG o PDF.', 'danger')
        return redirect(request.url)