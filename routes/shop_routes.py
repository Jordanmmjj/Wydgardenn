from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required
from models import db, Producto, Categoria, Carrito, Pedido, DetallePedido, Venta
from datetime import datetime
from flask_mail import Message

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/catalogo')
def catalogo():
    categoria_id = request.args.get('categoria')
    precio_min = request.args.get('precio_min', type=float)
    precio_max = request.args.get('precio_max', type=float)
    buscar = request.args.get('buscar', '')
    query = Producto.query
    if categoria_id: query = query.filter_by(categoria_id=categoria_id)
    if precio_min is not None: query = query.filter(Producto.precio >= precio_min)
    if precio_max is not None: query = query.filter(Producto.precio <= precio_max)
    if buscar: query = query.filter(Producto.nombre.ilike(f'%{buscar}%'))
    productos = query.all()
    categorias = Categoria.query.all()
    return render_template('catalogo.html', productos=productos, categorias=categorias)

@shop_bp.route('/carrito')
@login_required
def ver_carrito():
    items_carrito = Carrito.query.filter_by(id_usuario=current_user.id).all()
    total = sum(item.producto.precio * item.cantidad for item in items_carrito)
    return render_template('carrito.html', items_carrito=items_carrito, total=total)

@shop_bp.route('/carrito/agregar/<int:producto_id>', methods=['POST'])
@login_required
def agregar_al_carrito(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    if producto.stock <= 0: return "Producto agotado", 400
    item = Carrito.query.filter_by(id_usuario=current_user.id, id_producto=producto_id).first()
    if item:
        if item.cantidad < producto.stock: item.cantidad += 1
        else: return "Stock insuficiente", 400
    else:
        db.session.add(Carrito(id_usuario=current_user.id, id_producto=producto_id, cantidad=1))
    db.session.commit()
    return "OK", 200

@shop_bp.route('/carrito/eliminar/<int:carrito_id>', methods=['POST'])
@login_required
def eliminar_del_carrito(carrito_id):
    item = Carrito.query.get_or_404(carrito_id)
    if item.id_usuario == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash('Eliminado del carrito.', 'success')
    return redirect(url_for('shop.ver_carrito'))

@shop_bp.route('/carrito/actualizar/<int:carrito_id>', methods=['POST'])
@login_required
def actualizar_carrito(carrito_id):
    item = Carrito.query.get_or_404(carrito_id)
    nueva_cant = request.form.get('cantidad', type=int)
    if item.id_usuario == current_user.id and nueva_cant is not None:
        if nueva_cant > 0 and nueva_cant <= item.producto.stock:
            item.cantidad = nueva_cant
            db.session.commit()
        elif nueva_cant <= 0:
            db.session.delete(item)
            db.session.commit()
        else:
            flash(f"Solo hay {item.producto.stock} unidades disponibles de {item.producto.nombre}.", "error")
    return redirect(url_for('shop.ver_carrito'))

def verificar_alerta_stock(producto):
    from flask import current_app
    from flask_mail import Message
    from app import enviar_correo_async
    
    limite_stock = current_app.config.get('STOCK_MINIMO_ALERTA', 5)
    if producto.stock <= limite_stock:
        try:
            cuerpo_admin = f"""
            ⚠️ ¡ALERTA DE STOCK BAJO! 🌵
            
            Queremos informarte que el producto "{producto.nombre}" (ID: {producto.id}) tiene un nivel de stock bajo.
            
            -----------------------------------
            DETALLES DEL PRODUCTO
            -----------------------------------
            ID Producto: {producto.id}
            Nombre: {producto.nombre}
            Stock Actual: {producto.stock} unidades
            Precio: ${producto.precio:,.0f}
            
            Por favor, ingresa al panel de administración para reabastecer el inventario o actualizar/eliminar el producto.
            
            ¡Alerta del Sistema de WYDGARDEN!
            """
            msg = Message(
                subject=f"⚠️ Alerta de Stock Bajo: {producto.nombre} ({producto.stock} uds)",
                body=cuerpo_admin,
                recipients=[current_app.config.get('ADMIN_EMAIL', 'jordancely00@gmail.com')]
            )
            enviar_correo_async(msg)
            print(f"Correo de alerta de stock bajo enviado al administrador para: {producto.nombre} (async)")
        except Exception as e:
            print(f"Error al enviar correo de alerta de stock bajo para {producto.nombre}: {e}")

@shop_bp.route('/carrito/checkout', methods=['POST'])
@login_required
def checkout():
    items = Carrito.query.filter_by(id_usuario=current_user.id).all()
    if not items:
        flash('Tu carrito está vacío.', 'error')
        return redirect(url_for('shop.ver_carrito'))
    
    metodo_pago = request.form.get('metodoPago', 'EFECTIVO')
    total_pedido = sum(i.producto.precio * i.cantidad for i in items)
    
    nuevo_pedido = Pedido(id_usuario=current_user.id, total=total_pedido, estado='PENDIENTE', metodo_pago=metodo_pago)
    db.session.add(nuevo_pedido)
    db.session.flush() # Para obtener el ID
    
    productos_comprados = []
    for i in items:
        prod = i.producto
        if prod.stock < i.cantidad:
            flash(f'Error: El producto {prod.nombre} solo tiene {prod.stock} unidades.', 'error')
            db.session.rollback()
            return redirect(url_for('shop.ver_carrito'))
        
        detalle = DetallePedido(id_pedido=nuevo_pedido.id_pedido, id_producto=prod.id, cantidad=i.cantidad, precio_unitario=prod.precio, subtotal=prod.precio*i.cantidad)
        prod.stock -= i.cantidad
        productos_comprados.append((prod, i.cantidad))
        db.session.add(detalle)
        db.session.delete(i) # Borrar del carrito
        
    nueva_venta = Venta(id_usuario=current_user.id, total=total_pedido, id_pedido=nuevo_pedido.id_pedido)
    db.session.add(nueva_venta)
    
    db.session.commit()

    # Verificar alertas de stock bajo después del commit
    for prod, cant in productos_comprados:
        try:
            verificar_alerta_stock(prod)
        except Exception as e:
            print(f"Error al verificar alerta de stock durante checkout: {e}")

    try:
        from app import enviar_correo_async
        fecha_actual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        num_nequi = request.form.get('numeroNequi', 'No proporcionado')
        detalle_pago = f"Nequi: {num_nequi}" if metodo_pago == 'NEQUI' else "Efectivo"
        
        lista_productos = ""
        for prod, cant in productos_comprados:
            lista_productos += f"- {prod.nombre} x{cant}: ${prod.precio * cant:,.0f}\n"

        cuerpo_admin = f"""
        ¡Nueva venta realizada en WYDGARDEN!
        -----------------------------------
        ID Pedido: {nuevo_pedido.id_pedido}
        Cliente: {current_user.nombres} {current_user.apellidos}
        Email: {current_user.email}
        
        Fecha y Hora: {fecha_actual}
        Método de Pago: {metodo_pago}
        Detalle Pago: {detalle_pago}
        
        PRODUCTOS:
        {lista_productos}
        
        VALOR TOTAL: ${total_pedido:,.0f}
        -----------------------------------
        ¡Revisa el dashboard para empacar el pedido!
        """
        
        from flask import current_app
        msg_admin = Message(subject=f"🌵 Notificación de Venta #{nuevo_pedido.id_pedido}",
                           body=cuerpo_admin,
                           recipients=[current_app.config.get('ADMIN_EMAIL', 'jordan.cely06@gmail.com')])
        enviar_correo_async(msg_admin)

        instrucciones_pago = ""
        if metodo_pago == 'NEQUI':
            instrucciones_pago = f"""
        -----------------------------------
        INSTRUCCIONES DE PAGO (NEQUI)
        -----------------------------------
        Por favor realiza la transferencia de ${total_pedido:,.0f} 
        al número de la empresa: 3204910123
        Una vez realizado el pago, tu pedido será procesado.
        -----------------------------------
        """

        limite_horas = current_app.config.get('LIMITE_HORAS_EXPIRACION', 24)
        cuerpo_usuario = f"""
        🌵 ¡Hola {current_user.nombres}! Gracias por tu compra en WYDGARDEN.
        
        Tu pedido #{nuevo_pedido.id_pedido} ha sido registrado con éxito. 
        Aquí tienes los detalles de tu compra:
        {instrucciones_pago}
        -----------------------------------
        RESUMEN DE FACTURA
        -----------------------------------
        Fecha: {fecha_actual}
        Método de Pago: {metodo_pago}
        {f"Tu Número Nequi (Referencia): {num_nequi}" if metodo_pago == 'NEQUI' else ""}
        
        PRODUCTOS:
        {lista_productos}
        
        TOTAL A PAGAR: ${total_pedido:,.0f}
        -----------------------------------
        Estado del pedido: PENDIENTE DE VALIDACIÓN
        
        ⚠️ IMPORTANTE: Recuerda que tienes un plazo máximo de {limite_horas} horas para realizar el pago o recoger tu pedido. De lo contrario, se cancelará automáticamente para liberar los productos en stock.
        
        Estamos preparando tus productos. Te notificaremos cuando estén en camino.
        ¡Gracias por confiar en nosotros!
        """
        
        msg_usuario = Message(subject=f"🌵 Tu Factura de Compra WYDGARDEN #{nuevo_pedido.id_pedido}",
                             body=cuerpo_usuario,
                             recipients=[current_user.email])
        enviar_correo_async(msg_usuario)
        
        print(f"Correos de venta (admin y usuario) en cola de envío.")
    except Exception as e:
        print(f"Error al enviar correos: {e}")

    return render_template('compra_exitosa.html', total=total_pedido, id_pedido=nuevo_pedido.id_pedido, metodo_pago=metodo_pago)

