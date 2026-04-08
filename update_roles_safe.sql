UPDATE usuarios SET id_rol = (SELECT id_rol FROM roles WHERE nombre = 'ADMIN') WHERE correo = 'juan.perez@test.com';
UPDATE usuarios SET id_rol = (SELECT id_rol FROM roles WHERE nombre = 'CLIENTE') WHERE correo = 'maria.garcia@test.com';

-- Insertar empleado copiando la contraseña de Juan para que sea 'Test123456'
INSERT INTO usuarios (nombre, apellido, correo, telefono, contraseña, id_rol) 
SELECT 'Empleado', 'Test', 'empleado@test.com', '0000', u.contraseña, (SELECT id_rol FROM roles WHERE nombre='EMPLEADO')
FROM usuarios u WHERE u.correo = 'juan.perez@test.com'
AND NOT EXISTS (SELECT 1 FROM usuarios WHERE correo = 'empleado@test.com') LIMIT 1;
