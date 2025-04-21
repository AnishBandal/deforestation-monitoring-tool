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

// Process signup
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = trim($_POST["email"]);
    $password = trim($_POST["password"]);
    $confirm_password = trim($_POST["confirm_password"]);

    if (!empty($email) && !empty($password) && !empty($confirm_password)) {
        if ($password !== $confirm_password) {
            echo "<script>alert('Passwords do not match'); window.location.href='signup.php';</script>";
            exit();
        }

        // Check if email already exists
        $stmt = $conn->prepare("SELECT id FROM users WHERE email = ?");
        $stmt->bind_param("s", $email);
        $stmt->execute();
        $stmt->store_result();

        if ($stmt->num_rows > 0) {
            echo "<script>alert('Email already registered'); window.location.href='signup.php';</script>";
        } else {
            // Hash password
            $hashed_password = password_hash($password, PASSWORD_BCRYPT);

            // Insert into database
            $stmt = $conn->prepare("INSERT INTO users (email, password) VALUES (?, ?)");
            $stmt->bind_param("ss", $email, $hashed_password);
            if ($stmt->execute()) {
                $_SESSION["user_id"] = $stmt->insert_id;
                $_SESSION["email"] = $email;
                header("Location: dashboard.php");
                exit();
            } else {
                echo "<script>alert('Error creating account'); window.location.href='signup.php';</script>";
            }
        }

        $stmt->close();
    } else {
        echo "<script>alert('Please fill in all fields'); window.location.href='signup.php';</script>";
    }
}

$conn->close();
?>