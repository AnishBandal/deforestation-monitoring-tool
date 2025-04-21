<?php
session_start();
$host = "localhost";
$username = "root";
$password = "";
$dbname = "deforestation_monitoring";

// Connect to MySQL
$conn = new mysqli($host, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Process login
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = trim($_POST["email"]);
    $password = trim($_POST["password"]);

    if (!empty($email) && !empty($password)) {
        $stmt = $conn->prepare("SELECT id, password FROM users WHERE email = ?");
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $stmt->store_result();

        if ($stmt->num_rows > 0) {
            $stmt->bind_result($id, $hashed_password);
            $stmt->fetch();

            // Verify the password using bcrypt
            if (password_verify($password, $hashed_password)) {
                $_SESSION["user_id"] = $id;
                $_SESSION["email"] = $email;
                header("Location: dashboard.php");
                exit();
            } else {
                echo "<script>alert('Invalid Credentials'); window.location.href='index.php';</script>";
            }
        } else {
            echo "<script>alert('User not found'); window.location.href='index.php';</script>";
        }

        $stmt->close();
    } else {
        echo "<script>alert('Please fill in all fields'); window.location.href='index.php';</script>";
    }
}

$conn->close();
?>