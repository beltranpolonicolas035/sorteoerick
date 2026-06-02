import random
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from base_datos import db
from modelos import Compra, Boleta, Ganador
from flask_mail import Message
from extensiones import mail
# IMPORTACIÓN DEL PROTECTOR DE RUTAS
from auth import login_requerido 

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_requerido # RUTA PROTEGIDA
def admin():
    compras_pendientes = Compra.query.filter_by(estado='pendiente').order_by(Compra.fecha_creacion.desc()).all()
    
    total_pendientes = len(compras_pendientes)
    total_aprobados = Compra.query.filter_by(estado='confirmado').count()
    total_rechazados = Compra.query.filter_by(estado='rechazado').count()
    
    return render_template(
        'admin.html', 
        compras_pendientes=compras_pendientes,
        total_pendientes=total_pendientes,
        total_aprobados=total_aprobados,
        total_rechazados=total_rechazados
    )

@admin_bp.route('/admin/aprobar/<int:compra_id>', methods=['POST'])
@login_requerido # RUTA PROTEGIDA
def aprobar_compra(compra_id):
    compra = Compra.query.get_or_404(compra_id)
    
    if compra and compra.estado == 'pendiente':
        tickets_vendidos = db.session.query(Boleta.numero).filter_by(estado='vendido').all()
        numeros_ocupados = set([t.numero for t in tickets_vendidos])
        
        # Generar números disponibles (00000 al 99999)
        numeros_disponibles = [str(i).zfill(5) for i in range(100000) if str(i).zfill(5) not in numeros_ocupados]
        
        if len(numeros_disponibles) < compra.cantidad_tickets:
            flash("🛑 Error: No hay suficientes boletas disponibles.", "danger")
            return redirect(url_for('admin.admin'))
            
        numeros_suerte = random.sample(numeros_disponibles, compra.cantidad_tickets)
        
        for num in numeros_suerte:
            nueva_boleta = Boleta(numero=num, estado='vendido', compra_id=compra.id)
            db.session.add(nueva_boleta)
            
        compra.estado = 'confirmado'
        db.session.commit()
        
        try:
            msg = Message("¡Tus números de la rifa Zona B&R!", recipients=[compra.correo])
            msg.html = render_template('correo.html', 
                                        nombre_cliente=compra.nombre, 
                                        numeros=numeros_suerte)
            mail.send(msg)
            flash(f"✅ ¡Compra de {compra.nombre} aprobada! Se generaron {compra.cantidad_tickets} números y se envió el correo.", "success")
        except Exception as e:
            flash(f"⚠️ Compra aprobada, pero hubo un error enviando el correo: {e}", "warning")
        
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/rechazar/<int:compra_id>', methods=['POST'])
@login_requerido # RUTA PROTEGIDA
def rechazar_compra(compra_id):
    compra = Compra.query.get_or_404(compra_id)
    
    if compra and compra.estado == 'pendiente':
        compra.estado = 'rechazado'
        compra.comprobante_pago = None 
        db.session.commit()
        flash(f"❌ La compra de {compra.nombre} ha sido rechazada.", "danger")
        
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/historial', methods=['GET'])
@login_requerido # RUTA PROTEGIDA
def admin_historial():
    buscar_usuario = request.args.get('buscar_usuario', '')
    buscar_numero = request.args.get('buscar_numero', '')
    
    se_busco = bool(buscar_usuario or buscar_numero)
    query = Compra.query.filter(Compra.estado != 'pendiente')
    
    if buscar_usuario:
        query = query.filter((Compra.nombre.like(f"%{buscar_usuario}%")) | (Compra.cedula.like(f"%{buscar_usuario}%")))
    
    if buscar_numero:
        query = query.join(Boleta).filter(Boleta.numero == buscar_numero)
        
    usuarios_filtrados = query.order_by(Compra.fecha_creacion.desc()).all()
    
    return render_template(
        'historial.html', 
        usuarios_historial=usuarios_filtrados,
        buscar_usuario=buscar_usuario,
        buscar_numero=buscar_numero,
        se_busco=se_busco
    )

@admin_bp.route('/admin/reiniciar-sistema', methods=['POST'])
@login_requerido # RUTA PROTEGIDA
def reiniciar_sistema():
    try:
        # Limpieza de tablas (PostgreSQL compatible)
        # Usamos TRUNCATE con RESTART IDENTITY para borrar datos y resetear IDs a 1
        db.session.execute(db.text("TRUNCATE TABLE boletas RESTART IDENTITY CASCADE;"))
        db.session.execute(db.text("TRUNCATE TABLE compras RESTART IDENTITY CASCADE;"))
        db.session.execute(db.text("TRUNCATE TABLE ganador_oficial RESTART IDENTITY CASCADE;"))
        db.session.commit()
        
        # Limpieza de archivos físicos
        folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error borrando archivo {filename}: {e}")
        
        flash('¡Sistema restablecido correctamente en la nube!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al reiniciar: {str(e)}', 'danger')
        
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/publicar-ganador', methods=['POST'])
@login_requerido # RUTA PROTEGIDA
def publicar_ganador():
    nombre = request.form.get('nombre_ganador')
    numero = request.form.get('numero_ganador')
    premio = request.form.get('premio')
    
    if nombre and numero and premio:
        # Borramos al anterior ganador antes de publicar el nuevo
        db.session.execute(db.text("TRUNCATE TABLE ganador_oficial RESTART IDENTITY CASCADE;"))
        
        nuevo_ganador = Ganador(nombre=nombre, numero=numero, premio=premio)
        db.session.add(nuevo_ganador)
        db.session.commit()
        
        flash("🏆 ¡Ganador publicado con éxito!", "success")
    else:
        flash("⚠️ Todos los campos son obligatorios.", "danger")
        
    return redirect(url_for('admin.admin_historial'))