from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Pedido, DetallePedido, Venta, Producto
from datetime import datetime
from flask_mail import Message

pedidos_bp = Blueprint('pedidos', __name__)

def verificar_y_cancelar_pedidos_expirados():
    from datetime import datetime, timedelta
    from flask import current_app
    
    limite_horas = current_app.config.get('LIMITE_HORAS_EXPIRACION', 24)
    limite_tiempo = datetime.now() - timedelta(hours=limite_horas)
    
    # Obtener pedidos pendientes expirados
    pedidos_expirados = Pedido.query.filter(
        Pedido.estado == 'PENDIENTE',
        Pedido.fecha_pedido < limite_tiempo
    ).all()
    
    if not pedidos_expirados:
        return
        
    for pedido in pedidos_expirados:
        pedido.estado = 'CANCELADO'
        # Devolver stock
        for detalle in pedido.detalles:
            if detalle.producto:
                detalle.producto.stock += detalle.cantidad
                
        # Eliminar de ventas
        Venta.query.filter_by(id_pedido=pedido.id_pedido).delete()
        
        # Enviar correo de notificación
        try:
            from app import mail
            cuerpo_usuario = f"""
            🌵 ¡Hola {pedido.usuario.nombres}!
            
            Queremos informarte que tu pedido #{pedido.id_pedido} en WYDGARDEN ha sido cancelado automáticamente, debido a que superó el tiempo límite de {limite_horas} horas para realizar el pago o recoger los productos.
            
            -----------------------------------
            DETALLES DEL PEDIDO CANCELADO
            -----------------------------------
            ID Pedido: #{pedido.id_pedido}
            Fecha del Pedido: {pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M:%S')}
            Total: ${pedido.total:,.0f}
            
            Si aún deseas adquirir estos productos, por favor realiza una nueva compra en nuestro catálogo.
            
            ¡Gracias por tu interés en WYDGARDEN!
            """
            msg = Message(
                subject=f"🌵 Pedido #{pedido.id_pedido} Cancelado por Expiración",
                body=cuerpo_usuario,
                recipients=[pedido.usuario.email]
            )
            mail.send(msg)
            print(f"Pedido #{pedido.id_pedido} cancelado automáticamente por expiración.")
        except Exception as e:
            print(f"Error al enviar correo de expiración para pedido #{pedido.id_pedido}: {e}")
            
    db.session.commit()

@pedidos_bp.before_app_request
def antes_de_cualquier_peticion():
    from flask import request
    if request.endpoint and any(word in request.endpoint for word in ['shop.', 'pedidos.', 'admin.dashboard']):
        try:
            verificar_y_cancelar_pedidos_expirados()
        except Exception as e:
            print(f"Error al verificar pedidos expirados: {e}")

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
        
        # Caso 1: Se cancela un pedido que no estaba cancelado
        if nuevo_estado == 'CANCELADO' and estado_anterior != 'CANCELADO':
            # Devolver stock
            for detalle in pedido.detalles:
                if detalle.producto:
                    detalle.producto.stock += detalle.cantidad
            # Eliminar la venta asociada
            Venta.query.filter_by(id_pedido=pedido.id_pedido).delete()
            
        # Caso 2: Se reactiva un pedido que estaba cancelado
        elif nuevo_estado != 'CANCELADO' and estado_anterior == 'CANCELADO':
            # Verificar stock disponible para todos los productos
            for detalle in pedido.detalles:
                if detalle.producto and detalle.producto.stock < detalle.cantidad:
                    flash(f'No hay suficiente stock para reactivar el pedido. Producto "{detalle.producto.nombre}" solo tiene {detalle.producto.stock} unidades.', 'error')
                    return redirect(url_for('pedidos.admin_pedidos_list'))
            
            # Descontar stock
            for detalle in pedido.detalles:
                if detalle.producto:
                    detalle.producto.stock -= detalle.cantidad
                    # Verificar alertas de stock bajo al descontar
                    try:
                        from routes.shop_routes import verificar_alerta_stock
                        verificar_alerta_stock(detalle.producto)
                    except Exception as e:
                        print(f"Error al verificar alerta de stock al reactivar: {e}")
            
            # Crear de nuevo la venta si no existe
            venta_existente = Venta.query.filter_by(id_pedido=pedido.id_pedido).first()
            if not venta_existente:
                nueva_venta = Venta(id_usuario=pedido.id_usuario, total=pedido.total, id_pedido=pedido.id_pedido)
                db.session.add(nueva_venta)
                
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

