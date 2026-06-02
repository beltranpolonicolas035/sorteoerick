import random
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from base_datos import db
from modelos import Compra, Boleta, Ganador
from flask_mail import Message
from extensiones import mail
from auth import login_requerido 

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_requerido
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
@login_requerido
def aprobar_compra(compra_id):
    try:
        compra = Compra.query.get_or_404(compra_id)
        if compra and compra.estado == 'pendiente':
            
            # Generación de números ocupados
            ocupados = {b[0] for b in db.session.query(Boleta.numero).all()}
            
            numeros_suerte = []
            while len(numeros_suerte) < compra.cantidad_tickets:
                num = f"{random.randint(0, 99999):05d}"
                if num not in ocupados:
                    numeros_suerte.append(num)
                    ocupados.add(num)
            
            # Guardado en DB
            boletas_nuevas = [Boleta(numero=n, estado='vendido', compra_id=compra.id) for n in numeros_suerte]
            db.session.add_all(boletas_nuevas)
            compra.estado = 'confirmado'
            db.session.commit()
            
            # Envío de correo optimizado para evitar bloqueos del servidor
            try:
                with mail.connect() as conn:
                    msg = Message("¡Tus números de la rifa!", recipients=[compra.correo])
                    msg.body = f"Hola {compra.nombre}, tus números son: {', '.join(numeros_suerte)}"
                    conn.send(msg)
                flash(f"✅ Compra de {compra.nombre} aprobada y correo enviado.", "success")
            except Exception as e:
                # Si el correo falla, no cancelamos la aprobación. Solo avisamos.
                print(f"ERROR EN ENVÍO: {str(e)}")
                flash(f"✅ Compra aprobada (aviso: error al enviar correo).", "warning")
            
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error al procesar: {str(e)}", "danger")
        
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/rechazar/<int:compra_id>', methods=['POST'])
@login_requerido
def rechazar_compra(compra_id):
    compra = Compra.query.get_or_404(compra_id)
    if compra and compra.estado == 'pendiente':
        compra.estado = 'rechazado'
        compra.comprobante_pago = None 
        db.session.commit()
        flash(f"❌ La compra de {compra.nombre} ha sido rechazada.", "danger")
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/historial', methods=['GET'])
@login_requerido
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
@login_requerido
def reiniciar_sistema():
    try:
        db.session.execute(db.text("TRUNCATE TABLE boletas RESTART IDENTITY CASCADE;"))
        db.session.execute(db.text("TRUNCATE TABLE compras RESTART IDENTITY CASCADE;"))
        db.session.execute(db.text("TRUNCATE TABLE ganador_oficial RESTART IDENTITY CASCADE;"))
        db.session.commit()
        
        folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path): os.unlink(file_path)
        
        flash('¡Sistema restablecido!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al reiniciar: {str(e)}', 'danger')
    return redirect(url_for('admin.admin'))

@admin_bp.route('/admin/publicar-ganador', methods=['POST'])
@login_requerido
def publicar_ganador():
    nombre = request.form.get('nombre_ganador')
    numero = request.form.get('numero_ganador')
    premio = request.form.get('premio')
    
    if nombre and numero and premio:
        db.session.execute(db.text("TRUNCATE TABLE ganador_oficial RESTART IDENTITY CASCADE;"))
        db.session.add(Ganador(nombre=nombre, numero=numero, premio=premio))
        db.session.commit()
        flash("🏆 ¡Ganador publicado!", "success")
    else:
        flash("⚠️ Campos obligatorios.", "danger")
    return redirect(url_for('admin.admin_historial'))