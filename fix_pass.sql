UPDATE usuarios 
SET contraseña = (
    SELECT contraseña FROM (SELECT * FROM usuarios WHERE correo = 'juan.perez@test.com') AS tmp
)
WHERE correo = 'jordan@admin.com';
