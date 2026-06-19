from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Pedido, DetallePedido
from datetime import datetime
from flask_mail import Message

pedidos_bp = Blueprint('pedidos', __name__)

@pedidos_bp.route('/mis-pedidos')
@login_required
def mis_pedidos():
    # Obtiene todos los pedidos del usuario actual ordenados por fecha descendente
    lista_pedidos = Pedido.query.filter_by(id_usuario=current_user.id).order_by(Pedido.fecha_pedido.desc()).all()
    return render_template('mis_pedidos.html', lista_pedidos=lista_pedidos)

@pedidos_bp.route('/admin/pedidos')
@login_required
def admin_pedidos_list():
    if current_user.rol.nombre not in ['ADMIN', 'EMPLEADO']:
        return "Acceso denegado", 403
    
    # Obtiene todos los pedidos registrados en el sistema
    lista_pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all()
    return render_template('admin/pedidos/lista.html', lista_pedidos=lista_pedidos)

@pedidos_bp.route('/admin/pedidos/actualizar-estado/<int:pedido_id>', methods=['POST'])
@login_required
def actualizar_estado(pedido_id):
    if current_user.rol.nombre not in ['ADMIN', 'EMPLEADO']:
        return "Acceso denegado", 403
        
    pedido = Pedido.query.get_or_404(pedido_id)
    nuevo_estado = request.form.get('estado')
    
    if nuevo_estado in ['PENDIENTE', 'PROCESANDO', 'ENVIADO', 'ENTREGADO', 'CANCELADO']:
        estado_anterior = pedido.estado
        pedido.estado = nuevo_estado
        db.session.commit()
        flash(f'Estado del pedido #{pedido.id_pedido} actualizado de {estado_anterior} a {nuevo_estado} exitosamente.', 'success')
        
        # Enviar correo de notificación al usuario sobre el cambio de estado
        try:
            from app import mail
            cuerpo_usuario = f"""
            🌵 ¡Hola {pedido.usuario.nombres}!
            
            Queremos informarte que el estado de tu pedido #{pedido.id_pedido} en WYDGARDEN ha sido actualizado.
            
            -----------------------------------
            DETALLES DEL CAMBIO
            -----------------------------------
            Nuevo Estado: {nuevo_estado}
            Fecha de Actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            
            -----------------------------------
            RESUMEN DEL PEDIDO
            -----------------------------------
            ID Pedido: {pedido.id_pedido}
            Fecha del Pedido: {pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M:%S')}
            Método de Pago: {pedido.metodo_pago}
            Total: ${pedido.total:,.0f}
            
            Puedes ingresar a tu cuenta de WYDGARDEN en la sección "Mis Pedidos" para ver el detalle y seguir el estado de tu compra.
            
            ¡Gracias por preferir a WYDGARDEN!
            """
            
            msg = Message(subject=f"🌵 Actualización de Pedido #{pedido.id_pedido} - {nuevo_estado}",
                          body=cuerpo_usuario,
                          recipients=[pedido.usuario.email])
            mail.send(msg)
            print(f"Correo de actualización de estado enviado a {pedido.usuario.email}")
        except Exception as e:
            print(f"Error al enviar correo de actualización de estado: {e}")
            
    else:
        flash('Estado no válido.', 'error')
        
    return redirect(url_for('pedidos.admin_pedidos_list'))
