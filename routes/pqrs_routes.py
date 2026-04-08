from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Pqrs, Usuario
from datetime import datetime

pqrs_bp = Blueprint('pqrs', __name__)

@pqrs_bp.route('/pqrs', methods=['GET', 'POST'])
@login_required
def pqrs():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        mensaje = request.form.get('mensaje')
        
        # En el formulario original piden nombre y correo, pero como ya está logueado, lo tomamos del current_user
        nueva_pqrs = Pqrs(
            id_usuario=current_user.id,
            nombre=current_user.nombres,
            correo=current_user.email,
            tipo=tipo,
            mensaje=mensaje,
            estado='PENDIENTE',
            fecha=datetime.now()
        )
        
        db.session.add(nueva_pqrs)
        db.session.commit()
        
        flash('Tu solicitud ha sido enviada exitosamente. Pronto recibirás una respuesta.', 'success')
        return redirect(url_for('pqrs.mis_pqrs'))
        
    return render_template('pqrs.html')

@pqrs_bp.route('/pqrs/enviar', methods=['POST'])
@login_required
def enviar_pqrs():
    # Helper por si el form apunta a esta ruta específica
    return pqrs()

@pqrs_bp.route('/mis-pqrs')
@login_required
def mis_pqrs():
    lista_pqrs = Pqrs.query.filter_by(id_usuario=current_user.id).order_by(Pqrs.fecha.desc()).all()
    return render_template('mis_pqrs.html', listaPqrs=lista_pqrs)

@pqrs_bp.route('/admin/pqrs')
@login_required
def admin_pqrs_list():
    if current_user.rol.nombre not in ['ADMIN', 'EMPLEADO']:
        return "Acceso denegado", 403
    
    lista_pqrs = Pqrs.query.order_by(Pqrs.fecha.desc()).all()
    return render_template('admin/pqrs/lista.html', listaPqrs=lista_pqrs)

@pqrs_bp.route('/admin/pqrs/responder/<int:id>', methods=['GET', 'POST'])
@login_required
def responder_pqrs(id):
    if current_user.rol.nombre not in ['ADMIN', 'EMPLEADO']:
        return "Acceso denegado", 403
        
    pqrs_obj = Pqrs.query.get_or_404(id)
    
    if request.method == 'POST':
        respuesta = request.form.get('respuesta')
        pqrs_obj.respuesta = respuesta
        pqrs_obj.estado = 'RESPONDIDO'
        db.session.commit()
        
        flash('Respuesta enviada exitosamente.', 'success')
        return redirect(url_for('pqrs.admin_pqrs_list'))
        
    return render_template('admin/pqrs/responder.html', pqrs=pqrs_obj)

@pqrs_bp.route('/admin/pqrs/guardar-respuesta', methods=['POST'])
@login_required
def guardar_respuesta():
    # Helper por si el form apunta a esta ruta específica
    id_pqrs = request.form.get('id')
    return responder_pqrs(int(id_pqrs))
