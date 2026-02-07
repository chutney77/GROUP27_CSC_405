<?php
include "config.php";

if (isset($_POST['login'])) {

    $matric = mysqli_real_escape_string($conn, $_POST['matric_number']);

    $sql = "SELECT * FROM students WHERE matric_number = '$matric'";
    $result = mysqli_query($conn, $sql);

    if (mysqli_num_rows($result) == 1) {
        echo "Login successful";
        header("Location: dashboard.php");
    } else {
        echo "matric number does not exist";
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Student Login</title>
        <link rel ="stylesheet" href="signup.css">
</head>
<body>

<h2>Student Login</h2>

<form action="login.php" method="post">
    <input type="text" name="matric_number" placeholder="Matric Number" required><br><br>

    <input type="submit" name="login" value="LOGIN">
</form>

</body>
</html>
