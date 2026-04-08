from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, Response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Venta, DetallePedido, Pedido, Producto, Categoria
from datetime import datetime, date, timedelta
from routes.report_service import generar_pdf_ventas

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol.nombre not in ['ADMIN', 'EMPLEADO']:
        return "Acceso denegado", 403
        
    today = date.today()
    
    # 1. Total Ventas Hoy
    ventas_hoy = Venta.query.filter(db.func.date(Venta.fecha_venta) == today).all()
    total_ventas_hoy = sum(v.total for v in ventas_hoy) if ventas_hoy else 0
    
    # 2. Productos Vendidos Hoy
    pedidos_ids = [v.id_pedido for v in ventas_hoy]
    detalles = DetallePedido.query.filter(DetallePedido.id_pedido.in_(pedidos_ids)).all() if pedidos_ids else []
    productos_vendidos = sum(d.cantidad for d in detalles) if detalles else 0
    
    # Meta Diaria 1M
    meta = 1000000
    porcentaje_ventas = min((total_ventas_hoy / meta) * 100, 100) if meta > 0 else 0
    
    return render_template('dashboard.html', 
                           totalVentasHoy=total_ventas_hoy, 
                           productosVendidos=productos_vendidos,
                           porcentajeVentas=porcentaje_ventas)

@admin_bp.route('/reportes/ahora')
@login_required
def reporte_hoy():
    if current_user.rol.nombre not in ['ADMIN', 'EMPLEADO']:
        return "No autorizado", 403
    
    today = date.today()
    ventas = Venta.query.filter(db.func.date(Venta.fecha_venta) == today).all()
    pdf_bytes = generar_pdf_ventas(ventas, f"DEL DIA {today.strftime('%d/%m/%Y')}")
    
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-disposition": f"attachment; filename=reporte_hoy_{today}.pdf"}
    )

@admin_bp.route('/reportes/semana')
@login_required
def reporte_semanal():
    if current_user.rol.nombre not in ['ADMIN', 'EMPLEADO']:
        return "No autorizado", 403
    
    hace_siete_dias = date.today() - timedelta(days=7)
    ventas = Venta.query.filter(Venta.fecha_venta >= hace_siete_dias).all()
    pdf_bytes = generar_pdf_ventas(ventas, "ULTIMOS 7 DIAS")
    
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-disposition": "attachment; filename=reporte_semanal.pdf"}
    )

@admin_bp.route('/admin/productos')
@login_required
def gention_productos():
    if current_user.rol.nombre != 'ADMIN':
         return "Acceso restringido", 403
    return render_template('admin_productos.html')

@admin_bp.route('/api/productos', methods=['GET'])
@login_required
def api_get_productos():
    if current_user.rol.nombre not in ['ADMIN', 'EMPLEADO']:
         return jsonify([]), 403
    productos = Producto.query.all()
    lista = []
    for p in productos:
        lista.append({
            'id_producto': p.id,
            'nombre': p.nombre,
            'precio': float(p.precio),
            'stock': p.stock,
            'descripcion': p.descripcion,
            'imagen': p.imagenUrl,
            'categoria': {'id_categoria': p.categoria_id, 'nombre': p.categoria.nombre if p.categoria else 'S/C'}
        })
    return jsonify(lista)

@admin_bp.route('/api/categorias', methods=['GET'])
@login_required
def api_get_categorias():
    categorias = Categoria.query.all()
    lista = [{'id_categoria': c.id, 'nombre': c.nombre} for c in categorias]
    return jsonify(lista)

@admin_bp.route('/api/productos', methods=['POST'])
@login_required
def api_save_producto():
    if current_user.rol.nombre != 'ADMIN':
         return jsonify({'error': 'No autorizado'}), 403
    data = request.get_json()
    new_p = Producto(
        nombre=data.get('nombre'),
        descripcion=data.get('descripcion'),
        precio=data.get('precio'),
        stock=data.get('stock'),
        imagenUrl=data.get('imagen'),
        categoria_id=data.get('categoria', {}).get('id_categoria')
    )
    db.session.add(new_p)
    db.session.commit()
    return jsonify({'id_producto': new_p.id}), 201

@admin_bp.route('/api/productos/<int:id>', methods=['GET'])
@login_required
def api_get_producto_one(id):
    p = Producto.query.get_or_404(id)
    return jsonify({
        'id_producto': p.id,
        'nombre': p.nombre,
        'precio': float(p.precio),
        'stock': p.stock,
        'descripcion': p.descripcion,
        'imagen': p.imagenUrl,
        'categoria': {'id_categoria': p.categoria_id}
    })

@admin_bp.route('/api/productos/<int:id>', methods=['PUT'])
@login_required
def api_update_producto(id):
    if current_user.rol.nombre != 'ADMIN':
         return jsonify({'error': 'No autorizado'}), 403
    p = Producto.query.get_or_404(id)
    data = request.get_json()
    p.nombre = data.get('nombre')
    p.descripcion = data.get('descripcion')
    p.precio = data.get('precio')
    p.stock = data.get('stock')
    p.imagenUrl = data.get('imagen')
    p.categoria_id = data.get('categoria', {}).get('id_categoria')
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/api/productos/<int:id>', methods=['DELETE'])
@login_required
def api_delete_producto(id):
    if current_user.rol.nombre != 'ADMIN':
         return jsonify({'error': 'No autorizado'}), 403
    p = Producto.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'success': True})
