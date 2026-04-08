from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column('id_rol', db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column('id_usuario', db.Integer, primary_key=True)
    nombres = db.Column('nombre', db.String(100), nullable=False)
    apellidos = db.Column('apellido', db.String(100), nullable=False)
    email = db.Column('correo', db.String(100), unique=True, nullable=False)
    password = db.Column('password', db.String(255), nullable=False)
    telefono = db.Column(db.String(20))
    
    rol_id = db.Column('id_rol', db.Integer, db.ForeignKey('roles.id_rol'))
    rol = db.relationship('Rol', backref=db.backref('usuarios', lazy=True))

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column('id_categoria', db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column('id_producto', db.Integer, primary_key=True)
    nombre = db.Column('nombre', db.String(100), nullable=False)
    descripcion = db.Column('descripcion', db.Text)
    precio = db.Column('precio', db.Float, nullable=False)
    stock = db.Column('stock', db.Integer, nullable=False)
    imagenUrl = db.Column('imagen', db.String(255))
    
    categoria_id = db.Column('id_categoria', db.Integer, db.ForeignKey('categorias.id_categoria'))
    categoria = db.relationship('Categoria', backref=db.backref('productos', lazy=True))

class Carrito(db.Model):
    __tablename__ = 'carrito'
    id_carrito = db.Column('id_carrito', db.Integer, primary_key=True)
    id_usuario = db.Column('id_usuario', db.Integer, db.ForeignKey('usuarios.id_usuario'))
    id_producto = db.Column('id_producto', db.Integer, db.ForeignKey('productos.id_producto'))
    cantidad = db.Column('cantidad', db.Integer)

    usuario = db.relationship('Usuario', backref=db.backref('carritos', lazy=True))
    producto = db.relationship('Producto', backref=db.backref('carritos', lazy=True))

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id_pedido = db.Column('id_pedido', db.Integer, primary_key=True)
    id_usuario = db.Column('id_usuario', db.Integer, db.ForeignKey('usuarios.id_usuario'))
    fecha_pedido = db.Column('fecha_pedido', db.DateTime, default=datetime.utcnow)
    total = db.Column('total', db.Float)
    estado = db.Column('estado', db.String(50), default='PENDIENTE')
    metodo_pago = db.Column('metodo_pago', db.String(100))

    usuario = db.relationship('Usuario', backref=db.backref('pedidos', lazy=True))

class DetallePedido(db.Model):
    __tablename__ = 'detalles_pedido'
    id_detalle = db.Column('id_detalle', db.Integer, primary_key=True)
    id_pedido = db.Column('id_pedido', db.Integer, db.ForeignKey('pedidos.id_pedido'))
    id_producto = db.Column('id_producto', db.Integer, db.ForeignKey('productos.id_producto'))
    cantidad = db.Column('cantidad', db.Integer)
    precio_unitario = db.Column('precio_unitario', db.Float)
    subtotal = db.Column('subtotal', db.Float)

    pedido = db.relationship('Pedido', backref=db.backref('detalles', lazy=True))
    producto = db.relationship('Producto', backref=db.backref('detalles_pedido', lazy=True))

class Pqrs(db.Model):
    __tablename__ = 'pqrs'
    id_pqrs = db.Column('id_pqrs', db.Integer, primary_key=True)
    nombre = db.Column('nombre', db.String(255))
    correo = db.Column('correo', db.String(255))
    tipo = db.Column('tipo', db.String(100))
    mensaje = db.Column('mensaje', db.Text)
    fecha = db.Column('fecha', db.DateTime, default=datetime.utcnow)
    respuesta = db.Column('respuesta', db.Text)
    estado = db.Column('estado', db.String(50), default='PENDIENTE')

class Venta(db.Model):
    __tablename__ = 'ventas'
    id_venta = db.Column('id_venta', db.Integer, primary_key=True)
    id_usuario = db.Column('id_usuario', db.Integer, db.ForeignKey('usuarios.id_usuario'))
    fecha_venta = db.Column('fecha_venta', db.DateTime, default=datetime.utcnow)
    total = db.Column('total', db.Float)
    id_pedido = db.Column('id_pedido', db.Integer, db.ForeignKey('pedidos.id_pedido'))

    usuario = db.relationship('Usuario', backref=db.backref('ventas', lazy=True))
    pedido = db.relationship('Pedido', backref=db.backref('ventas', lazy=True))
