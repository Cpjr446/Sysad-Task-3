<?php
$servername = "localhost";
$username = "root";
$password = "mypass";
$dbname = "sql_injection_demo";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
