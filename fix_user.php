<?php
$mysqli = new mysqli("localhost", "root", "", "wydgarden");

if ($mysqli->connect_errno) {
    echo "Fallo al conectar a MySQL: " . $mysqli->connect_error;
    exit();
}

// 1. Obtener pass de Juan
$res = $mysqli->query("SELECT contraseña FROM usuarios WHERE correo = 'juan.perez@test.com'");
if (!$res) {
    echo "Error buscando a Juan: " . $mysqli->error;
    exit();
}
$row = $res->fetch_assoc();
if (!$row) {
    echo "Juan no encontrado.\n";
    exit();
}
$pass = $row['contraseña'];

echo "Pass de Juan obtenido (len " . strlen($pass) . ").\n";

// 2. Actualizar Jordan
$stmt = $mysqli->prepare("UPDATE usuarios SET contraseña = ?, id_rol = 1 WHERE correo = 'jordan@admin.com'");
$stmt->bind_param("s", $pass);
if ($stmt->execute()) {
    echo "Usuario Jordan actualizado a ADMIN con pass de Juan.\n";
} else {
    echo "Error actualizando: " . $stmt->error . "\n";
}
?>
