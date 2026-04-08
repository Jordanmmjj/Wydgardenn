<?php
$mysqli = new mysqli("localhost", "root", "", "wydgarden");

// Copiar contraseña de Juan Perez (que sabemos es 'Test123456') a Jordan Cely
$sql = "UPDATE usuarios 
        SET contraseña = (SELECT contraseña FROM (SELECT contraseña FROM usuarios WHERE correo = 'juan.perez@test.com') as tmp)
        WHERE correo = 'jordancely@admin.com'";

if ($mysqli->query($sql)) {
    echo "Contraseña reseteada correctamente. Ahora es: Test123456";
} else {
    echo "Error: " . $mysqli->error;
}
?>