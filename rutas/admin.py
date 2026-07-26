import random
import os
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from base_datos import db
from modelos import Compra, Boleta, Ganador
from flask_mail import Message
from extensiones import mail
from auth import login_requerido 

admin_bp = Blueprint('admin', __name__)

PRECIO_POR_TICKET = 200  # Debe coincidir con static/js/selection.js

@admin_bp.route('/admin')
@login_requerido
def admin():
    compras_pendientes = Compra.query.filter_by(estado='pendiente').order_by(Compra.fecha_creacion.desc()).all()
    total_pendientes = len(compras_pendientes)
    total_aprobados = Compra.query.filter_by(estado='confirmado').count()
    total_rechazados = Compra.query.filter_by(estado='rechazado').count()
    numeros_vendidos = Boleta.query.filter_by(estado='vendido').count()

    # --- Cálculo de recaudo ---
    # Usamos UTC porque Compra.fecha_creacion se guarda con CURRENT_TIMESTAMP de
    # Postgres, que en servicios como Render está en UTC por defecto. Si comparamos
    # contra date.today() (hora local del servidor/tu equipo), en Colombia (UTC-5)
    # se puede desincronizar y "hoy" nunca coincide con lo guardado en la BD.
    hoy = datetime.now(timezone.utc).date()

    tickets_confirmados_total = db.session.query(
        db.func.coalesce(db.func.sum(Compra.cantidad_tickets), 0)
    ).filter(Compra.estado == 'confirmado').scalar()

    tickets_confirmados_hoy = db.session.query(
        db.func.coalesce(db.func.sum(Compra.cantidad_tickets), 0)
    ).filter(
        Compra.estado == 'confirmado',
        db.func.date(Compra.fecha_creacion) == hoy
    ).scalar()

    recaudado_hoy = tickets_confirmados_hoy * PRECIO_POR_TICKET
    recaudado_total = tickets_confirmados_total * PRECIO_POR_TICKET

    return render_template(
        'admin.html', 
        compras_pendientes=compras_pendientes,
        total_pendientes=total_pendientes,
        total_aprobados=total_aprobados,
        total_rechazados=total_rechazados,
        recaudado_hoy=recaudado_hoy,
        recaudado_total=recaudado_total,
        numeros_vendidos=numeros_vendidos
    )

@admin_bp.route('/admin/aprobar/<int:compra_id>', methods=['POST'])
@login_requerido
def aprobar_compra(compra_id):
    try:
        compra = Compra.query.get_or_404(compra_id)
        if compra and compra.estado == 'pendiente':
            
            ocupados = {b[0] for b in db.session.query(Boleta.numero).all()}
            
            numeros_suerte = []
            while len(numeros_suerte) < compra.cantidad_tickets:
                num = f"{random.randint(0, 99999):05d}"
                if num not in ocupados:
                    numeros_suerte.append(num)
                    ocupados.add(num)
            
            boletas_nuevas = [Boleta(numero=n, estado='vendido', compra_id=compra.id) for n in numeros_suerte]
            db.session.add_all(boletas_nuevas)
            compra.estado = 'confirmado'
            db.session.commit()
            
            try:
                remitente = current_app.config.get('MAIL_DEFAULT_SENDER')
                msg = Message(
                    subject="¡Tus números de la rifa!",
                    sender=remitente,
                    recipients=[compra.correo]
                )
                msg.html = render_template('correo.html', nombre=compra.nombre, numeros=numeros_suerte)
                mail.send(msg)
                flash(f"✅ Compra de {compra.nombre} aprobada y correo enviado.", "success")
            except Exception as e:
                print(f"ERROR SMTP DETALLADO: {str(e)}")
                flash(f"✅ Compra aprobada. (Aviso: Error al enviar correo, revisar logs)", "warning")
            
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
    buscar_usuario = request.args.get('buscar_usuario', '').strip()
    buscar_numero = request.args.get('buscar_numero', '').strip()
    
    se_busco = bool(buscar_usuario or buscar_numero)
    
    # Si se busca por número puntual, manejarlo por separado para evitar errores de JOIN
    if buscar_numero:
        boleta = Boleta.query.filter_by(numero=buscar_numero).first()
        if boleta:
            usuarios_filtrados = Compra.query.filter_by(id=boleta.compra_id).all()
        else:
            usuarios_filtrados = []
        return render_template(
            'historial.html',
            usuarios_historial=usuarios_filtrados,
            buscar_usuario=buscar_usuario,
            buscar_numero=buscar_numero,
            se_busco=se_busco
        )

    # Búsqueda por nombre o cédula
    query = Compra.query.filter(Compra.estado != 'pendiente')
    
    if buscar_usuario:
        query = query.filter(db.cast(Compra.cedula, db.String).ilike(f"%{buscar_usuario}%"))
        
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