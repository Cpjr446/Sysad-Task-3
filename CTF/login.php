<?php
include 'config.php';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // Construct the SQL query
    $sql = "SELECT * FROM users WHERE username='' OR '1'='1' -- ' AND password='anything'";
;

    $result = $conn->query($sql);

    // Check for query error
    if ($result === false) {
        echo "Error: " . $conn->error;
    } else {
        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            echo "Login successful!<br>";
            echo "Flag: " . $row['flag'];
        } else {
            echo "Invalid username or password.";
        }
    }
}
?>
