from models import db, Usuario, Producto, Categoria, Rol
from app import create_app
from sqlalchemy import text

app = create_app()

def migrar_datos():
    with app.app_context():
        # 0. Limpiar todo lo nuevo para empezar de cero
        db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        tablas_nuevas = ['usuarios', 'productos', 'categorias', 'roles', 'pqrs', 'ventas', 'pedidos', 'detalles_pedido', 'carrito']
        for t in tablas_nuevas:
            db.session.execute(text(f"TRUNCATE TABLE {t};"))
        db.session.commit()
        print("Tablas nuevas limpias.")

        try:
            # 1. MIGRAR ROLES
            db.session.execute(text("INSERT IGNORE INTO roles (id_rol, nombre) VALUES (1, 'ADMIN'), (2, 'USUARIO'), (3, 'EMPLEADO');"))
            db.session.commit()

            # 2. MIGRAR CATEGORIAS (Desde 'categoria' a 'categorias')
            # Intentamos leer de 'categoria' si existe
            try:
                categorias_viejas = db.session.execute(text("SELECT id_categoria, nombre FROM categoria;")).fetchall()
                for c in categorias_viejas:
                    db.session.add(Categoria(id=c[0], nombre=c[1]))
                db.session.commit()
                print(f"Migradas {len(categorias_viejas)} categorías.")
            except:
                # Si falló porque ya no existe la vieja, creamos por defecto
                db.session.add(Categoria(id=1, nombre='General'))
                db.session.commit()

            # 3. MIGRAR PRODUCTOS (Desde 'producto' a 'productos')
            try:
                prod_viejos = db.session.execute(text("SELECT * FROM producto;")).fetchall()
                cols_p = [c[0] for c in db.session.execute(text("SHOW COLUMNS FROM producto;")).fetchall()]
                for p in prod_viejos:
                    dp = dict(zip(cols_p, p))
                    db.session.add(Producto(
                        id=dp.get('id_producto'),
                        nombre=dp.get('Nombre') or dp.get('nombre'),
                        descripcion=dp.get('Descripcion') or dp.get('descripcion'),
                        precio=dp.get('precio'),
                        stock=dp.get('stock') or 0,
                        imagenUrl=dp.get('imagen'),
                        categoria_id=dp.get('id_categoria')
                    ))
                db.session.commit()
                print(f"Migrados {len(prod_viejos)} productos.")
            except Exception as e:
                print("Error productos:", e)

            # 4. MIGRAR USUARIOS (Desde 'usuario' a 'usuarios')
            try:
                usuarios_viejos = db.session.execute(text("SELECT * FROM usuario;")).fetchall()
                cols_u = [c[0] for c in db.session.execute(text("SHOW COLUMNS FROM usuario;")).fetchall()]
                for u in usuarios_viejos:
                    du = dict(zip(cols_u, u))
                    pwd = None
                    for k, v in du.items():
                        if "contrase" in k.lower() and v: pwd = v; break
                    db.session.add(Usuario(
                        id=du.get('id_usuario'),
                        nombres=du.get('Nombre'),
                        apellidos=du.get('Apellido'),
                        email=du.get('Correo'),
                        password=pwd or "Cambiar123",
                        telefono=du.get('Telefono'),
                        rol_id=du.get('id_rol') or 2
                    ))
                db.session.commit()
                print(f"Migrados {len(usuarios_viejos)} usuarios.")
            except Exception as e:
                print("Error usuarios:", e)

            # 5. BORRE FINAL DE TABLAS VIEJAS
            tablas_viejas = ['usuario', 'producto', 'rol', 'categoria', 'pedido', 'detalle_pedido', 'inventario', 'entrada_inventario', 'salida_inventario', 'reportes']
            for t in tablas_viejas:
                try: db.session.execute(text(f"DROP TABLE IF EXISTS {t};")); print(f"Borrada '{t}'.")
                except: pass
            db.session.commit()

        finally:
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            db.session.commit()

        print("\n¡LIMPIEZA Y MIGRACIÓN COMPLETADA! ✨🌵🏆")

if __name__ == '__main__':
    migrar_datos()
