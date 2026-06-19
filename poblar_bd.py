import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from models import db, Rol, Usuario, Categoria, Producto, Carrito, Pedido, DetallePedido, Pqrs, Venta
from sqlalchemy import text

app = create_app()

def poblar():
    with app.app_context():
        print("Iniciando la inserción de datos de prueba...")
        
        # Desactivar llaves foráneas para poder limpiar
        db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        
        # Limpiar las 9 tablas
        tablas = ['carrito', 'detalles_pedido', 'ventas', 'pedidos', 'pqrs', 'productos', 'categorias', 'usuarios', 'roles']
        for t in tablas:
            db.session.execute(text(f"TRUNCATE TABLE {t};"))
        db.session.commit()
        print("Tablas limpiadas con éxito.")
        
        # 1. Insertar Roles
        rol_admin = Rol(id=1, nombre='ADMIN')
        rol_usuario = Rol(id=2, nombre='USUARIO')
        rol_empleado = Rol(id=3, nombre='EMPLEADO')
        db.session.add_all([rol_admin, rol_usuario, rol_empleado])
        db.session.commit()
        print("1. Roles insertados.")
        
        # 2. Insertar Usuarios
        admin_email = app.config.get('ADMIN_EMAIL', 'jordancely00@gmail.com')
        support_email = app.config.get('MAIL_USERNAME', 'jordan.cely06@gmail.com')
        
        usuarios = [
            Usuario(
                id=1,
                nombres='Jordan',
                apellidos='Cely',
                email=admin_email,
                password=generate_password_hash('AdminWyd123*'),
                telefono='3204910123',
                rol_id=1
            ),
            Usuario(
                id=2,
                nombres='Juan',
                apellidos='Pérez',
                email='cliente@test.com',
                password=generate_password_hash('Cliente123*'),
                telefono='3001234567',
                rol_id=2
            ),
            Usuario(
                id=3,
                nombres='Diana',
                apellidos='Gómez',
                email='empleado@test.com',
                password=generate_password_hash('Empleado123*'),
                telefono='3119876543',
                rol_id=3
            ),
            Usuario(
                id=4,
                nombres='Maria',
                apellidos='Rodriguez',
                email='maria@test.com',
                password=generate_password_hash('Maria123*'),
                telefono='3156789012',
                rol_id=2
            )
        ]
        
        # Agregar el correo de soporte si es diferente
        if support_email != admin_email:
            usuarios.append(
                Usuario(
                    id=5,
                    nombres='Admin Soporte',
                    apellidos='Wydgarden',
                    email=support_email,
                    password=generate_password_hash('AdminWyd123*'),
                    telefono='3204910123',
                    rol_id=1
                )
            )
            
        db.session.add_all(usuarios)
        db.session.commit()
        print("2. Usuarios insertados.")
        
        # 3. Insertar Categorías
        cat1 = Categoria(id=1, nombre='Plantas de Interior')
        cat2 = Categoria(id=2, nombre='Suculentas y Cactus')
        cat3 = Categoria(id=3, nombre='Macetas y Decoración')
        cat4 = Categoria(id=4, nombre='Sustratos y Abonos')
        db.session.add_all([cat1, cat2, cat3, cat4])
        db.session.commit()
        print("3. Categorías insertadas.")
        
        # 4. Insertar Productos
        productos = [
            Producto(
                id=1,
                nombre='Monstera Deliciosa (Costilla de Adán)',
                descripcion='Planta de interior muy popular con hojas grandes y perforadas. Fácil cuidado.',
                precio=45000.0,
                stock=15,
                imagenUrl='monstera.jpg',
                categoria_id=1
            ),
            Producto(
                id=2,
                nombre='Cactus de Asiento de Suegra',
                descripcion='Cactus redondo con espinas amarillas brillantes. Requiere sol directo.',
                precio=25000.0,
                stock=4,
                imagenUrl='cactus_suegra.jpg',
                categoria_id=2
            ),
            Producto(
                id=3,
                nombre='Maceta de Cerámica Artesanal Gato',
                descripcion='Hermosa maceta esmaltada con forma de gato. Ideal para suculentas.',
                precio=18000.0,
                stock=20,
                imagenUrl='maceta_gato.jpg',
                categoria_id=3
            ),
            Producto(
                id=4,
                nombre='Sustrato Especial para Suculentas (2kg)',
                descripcion='Mezcla con excelente drenaje de arena, perlita y turba.',
                precio=12000.0,
                stock=50,
                imagenUrl='sustrato.jpg',
                categoria_id=4
            ),
            Producto(
                id=5,
                nombre='Planta de Serpiente (Sansevieria)',
                descripcion='Purificadora de aire, muy resistente. Ideal para principiantes.',
                precio=32000.0,
                stock=3,
                imagenUrl='sansevieria.jpg',
                categoria_id=1
            ),
            Producto(
                id=6,
                nombre='Suculenta Echeveria Elegans',
                descripcion='Suculenta en forma de rosa con tonos azulados y rosados.',
                precio=8000.0,
                stock=35,
                imagenUrl='echeveria.jpg',
                categoria_id=2
            )
        ]
        db.session.add_all(productos)
        db.session.commit()
        print("4. Productos insertados.")
        
        # 5. Insertar Carrito
        item_carrito = Carrito(id_carrito=1, id_usuario=2, id_producto=1, cantidad=2)
        db.session.add(item_carrito)
        db.session.commit()
        print("5. Carrito insertado.")
        
        # 6. Insertar Pedidos
        ahora = datetime.now()
        pedidos = [
            Pedido(
                id_pedido=1,
                id_usuario=2,
                fecha_pedido=ahora - timedelta(days=2),
                total=90000.0,
                estado='ENTREGADO',
                metodo_pago='NEQUI'
            ),
            Pedido(
                id_pedido=2,
                id_usuario=4,
                fecha_pedido=ahora - timedelta(hours=12),
                total=58000.0,
                estado='PENDIENTE',
                metodo_pago='EFECTIVO'
            ),
            Pedido(
                id_pedido=3,
                id_usuario=2,
                fecha_pedido=ahora - timedelta(hours=26),
                total=18000.0,
                estado='PENDIENTE',
                metodo_pago='NEQUI'
            )
        ]
        db.session.add_all(pedidos)
        db.session.commit()
        print("6. Pedidos insertados.")
        
        # 7. Insertar Detalles de Pedidos
        detalles = [
            DetallePedido(id_detalle=1, id_pedido=1, id_producto=1, cantidad=2, precio_unitario=45000.0, subtotal=90000.0),
            DetallePedido(id_detalle=2, id_pedido=2, id_producto=5, cantidad=1, precio_unitario=32000.0, subtotal=32000.0),
            DetallePedido(id_detalle=3, id_pedido=2, id_producto=3, cantidad=1, precio_unitario=18000.0, subtotal=18000.0),
            DetallePedido(id_detalle=4, id_pedido=2, id_producto=6, cantidad=1, precio_unitario=8000.0, subtotal=8000.0),
            DetallePedido(id_detalle=5, id_pedido=3, id_producto=3, cantidad=1, precio_unitario=18000.0, subtotal=18000.0)
        ]
        db.session.add_all(detalles)
        db.session.commit()
        print("7. Detalles de Pedidos insertados.")
        
        # 8. Insertar PQRS
        mensajes_pqrs = [
            Pqrs(
                id_pqrs=1,
                id_usuario=2,
                nombre='Juan Pérez',
                correo='cliente@test.com',
                tipo='Duda',
                mensaje='¿Tienen envíos para la ciudad de Medellín?',
                fecha=ahora - timedelta(days=3),
                respuesta='Hola Juan, sí realizamos envíos nacionales a todo el país incluyendo Medellín.',
                estado='RESPONDIDO'
            ),
            Pqrs(
                id_pqrs=2,
                id_usuario=4,
                nombre='Maria Rodriguez',
                correo='maria@test.com',
                tipo='Reclamo',
                mensaje='Mi planta llegó un poco maltratada de una hoja.',
                fecha=ahora - timedelta(days=1),
                respuesta=None,
                estado='PENDIENTE'
            )
        ]
        db.session.add_all(mensajes_pqrs)
        db.session.commit()
        print("8. PQRS insertadas.")
        
        # 9. Insertar Ventas
        ventas = [
            Venta(
                id_venta=1,
                id_usuario=2,
                fecha_venta=ahora - timedelta(days=2),
                total=90000.0,
                id_pedido=1
            ),
            Venta(
                id_venta=2,
                id_usuario=4,
                fecha_venta=ahora - timedelta(hours=12),
                total=58000.0,
                id_pedido=2
            ),
            Venta(
                id_venta=3,
                id_usuario=2,
                fecha_venta=ahora - timedelta(hours=26),
                total=18000.0,
                id_pedido=3
            )
        ]
        db.session.add_all(ventas)
        db.session.commit()
        print("9. Ventas insertadas.")
        
        # Volver a activar llaves foráneas
        db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        db.session.commit()
        
        print("\n*** BASE DE DATOS POBLADA EXITOSAMENTE ***")

if __name__ == '__main__':
    poblar()
