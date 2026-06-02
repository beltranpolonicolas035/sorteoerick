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
            # Optimizamos para no cargar 100k elementos en memoria
            tickets_existentes = db.session.query(Boleta.numero).all()
            numeros_ocupados = {t.numero for t in tickets_existentes}
            
            numeros_suerte = []
            intentos = 0
            # Generamos números aleatorios hasta completar la cantidad solicitada
            while len(numeros_suerte) < compra.cantidad_tickets and intentos < 200000:
                num = str(random.randint(0, 99999)).zfill(5)
                if num not in numeros_ocupados:
                    numeros_suerte.append(num)
                    numeros_ocupados.add(num)
                intentos += 1
            
            if len(numeros_suerte) < compra.cantidad_tickets:
                flash("🛑 Error: No se pudieron generar suficientes números únicos.", "danger")
                return redirect(url_for('admin.admin'))
            
            # Inserción eficiente
            boletas_nuevas = [Boleta(numero=num, estado='vendido', compra_id=compra.id) for num in numeros_suerte]
            db.session.add_all(boletas_nuevas)
                
            compra.estado = 'confirmado'
            db.session.commit()
            
            # Envío de correo protegido
            try:
                msg = Message("¡Tus números de la rifa Zona B&R!", recipients=[compra.correo])
                msg.html = render_template('correo.html', nombre_cliente=compra.nombre, numeros=numeros_suerte)
                mail.send(msg)
                flash(f"✅ ¡Compra de {compra.nombre} aprobada!", "success")
            except Exception as e:
                print(f"Error al enviar correo: {e}")
                flash(f"✅ Compra aprobada, pero hubo problemas enviando el correo.", "warning")
            
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error crítico al procesar la compra: {str(e)}", "danger")
        
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
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error borrando archivo {filename}: {e}")
        
        flash('¡Sistema restablecido correctamente!', 'success')
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
        nuevo_ganador = Ganador(nombre=nombre, numero=numero, premio=premio)
        db.session.add(nuevo_ganador)
        db.session.commit()
        flash("🏆 ¡Ganador publicado con éxito!", "success")
    else:
        flash("⚠️ Todos los campos son obligatorios.", "danger")
        
    return redirect(url_for('admin.admin_historial'))