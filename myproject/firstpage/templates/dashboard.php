<?php
session_start();

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Student Information</title>
    <link rel="stylesheet" href="dashboard.css">

</head>
<body>

<div class="main-body"> 
<header>
    <nav class="top-navbar">
        <div class="nav-left">
            <span class="logo"> 
            <img src="main-logo.png">
            </span>
        </div>
        <div class="nav-right">
            <a class="dashboard" href="dashboard.php">Dashboard</a>
            <a class="dashboard" href="about.php">About</a>
            <a class="dashboard" href="logout.php">Logout</a>
        </div>
    </nav>
</header>

<h1 class="std">Student Information</h1>

<form method="POST" action="save_info.php" onsubmit="return prepareData()">

    <!-- BASIC INFO -->
    <div class="input-box">
        <label>Level</label><br>
        <select name="level" required>
            <option value="">Select Level</option>
            <option>100</option>
            <option>200</option>
            <option>300</option>
            <option>400</option>
        </select>
    </div>

    <div class="input-box">
        <label>CGPA</label><br>
        <input type="text"  min="0.1" max="5.00" name="cgpa" required>
    </div>

    <div class="input-box">
        <label>Failed Courses</label><br>
        <input type="text" name="failed_courses" placeholder="e.g. MTH101, CSC102">
    </div>

    <div class="input-box">
        <label>Department</label><br>
        <select name="department" required>
            <option value="">Select Department</option>
            <option>Computer Science</option>
            <option>Cyber Security</option>
            <option>Software Engineering</option>
            <option>Microbiology</option>
            <option>Biochemistry</option>
            <option>Industrial Chemistry</option>
        </select>
    </div>

    <!-- PAST COURSES -->
    <h2>Past Courses</h2>
    <button type="button" onclick="toggleDropdown('pastDropdown')">
        Add / View Past Courses ▼
    </button>

    <div id="pastDropdown" class="dropdown-content">
        <table id="pastTable">
            <tr>
                <th>Course</th>
                <th>Grade</th>
            </tr>
        </table>
        <button type="button" onclick="addPastRow()">+ Add Course</button>
    </div>

    <!-- CURRENT COURSES -->
    <h2>Current Courses</h2>
    <button type="button" onclick="toggleDropdown('currentDropdown')">
        Add / View Current Courses ▼
    </button>

    <div id="currentDropdown" class="dropdown-content">
        <table id="currentTable">
            <tr>
                <th>Course</th>
                <th>Status</th>
            </tr>
        </table>
        <button type="button" onclick="addCurrentRow()">+ Add Course</button>
    </div>

    
    <input type="hidden" name="past_courses" id="past_courses">
    <input type="hidden" name="current_courses" id="current_courses">

    <br>
<div style="text-align: right; margin-top: 20px;">
    <button type="submit"  class="save-btn">Save Information</button>
     <button type="submit" class="save-btn">Advice/Recommendation</button>
</div>

</form>
</div>

<script>
const MIN_COURSES = 6;
const MAX_COURSES = 9;

function toggleDropdown(id) {
    const el = document.getElementById(id);
    el.style.display = el.style.display === "block" ? "none" : "block";
}

function addPastRow() {
    const table = document.getElementById("pastTable");
    if (table.rows.length - 1 >= MAX_COURSES) return alert("Max courses reached");

    const row = table.insertRow();
    row.innerHTML = `
        <td><input type="text" required></td>
        <td><input type="text" required></td>
    `;
}

function addCurrentRow() {
    const table = document.getElementById("currentTable");
    if (table.rows.length - 1 >= MAX_COURSES) return alert("Max courses reached");

    const row = table.insertRow();
    row.innerHTML = `
        <td><input type="text" required></td>
        <td>
            <select required>
                <option value="">Select</option>
                <option>Registered</option>
                <option>In Progress</option>
                <option>Carried Over</option>
            </select>
        </td>
    `;
}

function prepareData() {
    let past = [];
    let current = [];

    document.querySelectorAll("#pastTable tr").forEach((row, i) => {
        if (i === 0) return;
        const inputs = row.querySelectorAll("input");
        if (inputs[0].value && inputs[1].value) {
            past.push({
                course: inputs[0].value,
                grade: inputs[1].value
            });
        }
    });

    document.querySelectorAll("#currentTable tr").forEach((row, i) => {
        if (i === 0) return;
        const course = row.querySelector("input");
        const status = row.querySelector("select");
        if (course.value && status.value) {
            current.push({
                course: course.value,
                status: status.value
            });
        }
    });

    document.getElementById("past_courses").value = JSON.stringify(past);
    document.getElementById("current_courses").value = JSON.stringify(current);

    return true;
}

// Initialize minimum rows
window.onload = () => {
    for (let i = 0; i < MIN_COURSES; i++) {
        addPastRow();
        addCurrentRow();
    }
};
</script>

</body>
</html>
