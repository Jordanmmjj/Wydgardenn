from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required
from models import db, Producto, Categoria, Carrito, Pedido, DetallePedido, Venta
from datetime import datetime

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
    return redirect(url_for('shop.ver_carrito'))

@shop_bp.route('/carrito/checkout', methods=['POST'])
@login_required
def checkout():
    items = Carrito.query.filter_by(id_usuario=current_user.id).all()
    if not items:
        flash('Tu carrito está vacío.', 'error')
        return redirect(url_for('shop.ver_carrito'))
    
    metodo_pago = request.form.get('metodoPago', 'EFECTIVO')
    total_pedido = sum(i.producto.precio * i.cantidad for i in items)
    
    # 1. Crear Pedido
    nuevo_pedido = Pedido(id_usuario=current_user.id, total=total_pedido, estado='ENTREGADO', metodo_pago=metodo_pago)
    db.session.add(nuevo_pedido)
    db.session.flush() # Para obtener el ID
    
    # 2. Crear Detalles y bajar stock
    for i in items:
        prod = i.producto
        if prod.stock < i.cantidad:
            flash(f'Error: El producto {prod.nombre} solo tiene {prod.stock} unidades.', 'error')
            db.session.rollback()
            return redirect(url_for('shop.ver_carrito'))
        
        detalle = DetallePedido(id_pedido=nuevo_pedido.id_pedido, id_producto=prod.id, cantidad=i.cantidad, precio_unitario=prod.precio, subtotal=prod.precio*i.cantidad)
        prod.stock -= i.cantidad
        db.session.add(detalle)
        db.session.delete(i) # Borrar del carrito
        
    # 3. Registrar Venta (Para el Dashboard y Reportes)
    nueva_venta = Venta(id_usuario=current_user.id, total=total_pedido, id_pedido=nuevo_pedido.id_pedido)
    db.session.add(nueva_venta)
    
    db.session.commit()
    return render_template('compra_exitosa.html', total=total_pedido, id_pedido=nuevo_pedido.id_pedido)
