INSERT INTO roles (nombre) VALUES ('ADMIN') ON DUPLICATE KEY UPDATE nombre='ADMIN';
INSERT INTO roles (nombre) VALUES ('CLIENTE') ON DUPLICATE KEY UPDATE nombre='CLIENTE';
INSERT INTO roles (nombre) VALUES ('EMPLEADO') ON DUPLICATE KEY UPDATE nombre='EMPLEADO';

UPDATE usuarios 
SET id_rol = (SELECT id_rol FROM roles WHERE nombre = 'ADMIN')
WHERE correo = 'juan.perez@test.com';

INSERT INTO usuarios (nombre, apellido, correo, telefono, contraseña, id_rol)
SELECT 'Empleado', 'Prueba', 'empleado@test.com', '123456789', '$2a$10$X.s.w.X.x.x.x.x.x.x.x.ExampleHashForTest123456', (SELECT id_rol FROM roles WHERE nombre = 'EMPLEADO')
WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE correo = 'empleado@test.com');

UPDATE usuarios 
SET contraseña = (SELECT contraseña FROM usuarios WHERE correo = 'juan.perez@test.com' LIMIT 1)
WHERE correo = 'empleado@test.com';
