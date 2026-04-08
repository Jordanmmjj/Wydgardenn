USE wydgarden;
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Limpiamos las tablas nuevas antes del trasplante
TRUNCATE TABLE usuarios;
TRUNCATE TABLE productos;
TRUNCATE TABLE categorias;

-- 2. Trasplantamos Clientes
INSERT INTO usuarios (id_usuario, apellido, nombre, telefono, `contraseña`, correo, id_rol) 
SELECT id_usuario, Apellido, Nombre, Telefono, `contraseña`, Correo, id_rol FROM usuario;

-- 3. Trasplantamos Categorias
INSERT INTO categorias (id_categoria, nombre)
SELECT id_categoria, nombre FROM categoria;

-- 4. Trasplantamos Productos
INSERT INTO productos (id_producto, nombre, descripcion, precio, stock, id_categoria, imagen)
SELECT id_producto, nombre, descripcion, precio, stock, id_categoria, imagen FROM producto;

-- 5. Borramos las tablas repetidas
DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS producto;
DROP TABLE IF EXISTS rol;
DROP TABLE IF EXISTS categoria;
DROP TABLE IF EXISTS pedido;
DROP TABLE IF EXISTS detalle_pedido;
DROP TABLE IF EXISTS inventario;
DROP TABLE IF EXISTS entrada_inventario;
DROP TABLE IF EXISTS salida_inventario;
DROP TABLE IF EXISTS metodo_pago;
DROP TABLE IF EXISTS tipo_pqrs;
DROP TABLE IF EXISTS reportes;

SET FOREIGN_KEY_CHECKS = 1;
