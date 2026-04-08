<?php
$mysqli = new mysqli("localhost", "root", "", "wydgarden");
if ($mysqli->connect_errno)
    die("Error BD: " . $mysqli->connect_error);

$correoJordan = 'jordancely@admin.com';

// 1. Promover id=1 (ADMIN) a Jordan
// Asumimos que ID 1 es ADMIN y ID 2 es CLIENTE según lo visto antes.
$rolAdmin = 1;
$rolCliente = 2;

$stmt = $mysqli->prepare("UPDATE usuarios SET id_rol = ? WHERE correo = ?");
$stmt->bind_param("is", $rolAdmin, $correoJordan);
$stmt->execute();

if ($stmt->affected_rows > 0) {
    echo "Exito: Jordan Cely ($correoJordan) ahora es ADMIN.\n";
} else {
    // Verificar si ya era admin
    $res = $mysqli->query("SELECT id_rol FROM usuarios WHERE correo = '$correoJordan'");
    $row = $res->fetch_assoc();
    if ($row && $row['id_rol'] == $rolAdmin) {
        echo "Info: Jordan Cely ya era ADMIN.\n";
    } else {
        echo "Error: No se encontró al usuario Jordan Cely o no se pudo actualizar.\n";
    }
}

// 2. Degradarlos a todos los demas admins a CLIENTE
$stmt = $mysqli->prepare("UPDATE usuarios SET id_rol = ? WHERE id_rol = ? AND correo != ?");
$stmt->bind_param("iis", $rolCliente, $rolAdmin, $correoJordan);
$stmt->execute();

echo "Se han quitado permisos de ADMIN a otros " . $stmt->affected_rows . " usuarios.\n";
?>