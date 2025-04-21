<?php
session_start();
if (!isset($_SESSION["user_id"])) {
    header("Location: index.php");
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Deforestation Monitoring Tool | Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <?php include 'includes/navbar.php'; ?>

        <div class="container mt-5">
            <div class="card shadow-sm p-4">
                <h2 class="text-center">Get Deforestation Data</h2>
                <form id="dataForm">
                    <div class="mb-3">
                        <label for="latitude" class="form-label">Latitude</label>
                        <input type="text" class="form-control" name="latitude" id="latitude" placeholder="Enter Latitude" required>
                    </div>

                    <div class="mb-3">
                        <label for="longitude" class="form-label">Longitude</label>
                        <input type="text" class="form-control" name="longitude" id="longitude" placeholder="Enter Longitude" required>
                    </div>

                    <div class="mb-3">
                        <label for="distance" class="form-label">Distance (km)</label>
                        <input type="number" class="form-control" name="distance" id="distance" placeholder="Enter Distance" required>
                    </div>

                    <div class="mb-3">
                        <label for="year" class="form-label">Select Year</label>
                        <select class="form-select" name="year" id="year" required>
                            <option value="" disabled selected>Select a Year</option>
                            <?php
                            $currentYear = date("Y");
                            for ($year = $currentYear; $year >= 2000; $year--) {
                                echo "<option value='$year'>$year</option>";
                            }
                            ?>
                        </select>
                    </div>

                    <div class="text-center">
                        <button type="submit" class="btn btn-primary">Get Data</button>
                    </div>
                </form>
            </div>
        </div>

        <script>
        document.getElementById("dataForm").addEventListener("submit", function(event) {
            event.preventDefault();

            let latitude = document.getElementById("latitude").value;
            let longitude = document.getElementById("longitude").value;
            let distance = document.getElementById("distance").value;
            let year = document.getElementById("year").value;

            let apiUrl = `http://localhost:5000/getData?latitude=${latitude}&longitude=${longitude}&distance=${distance}&year=${year}`;

            // Open a new tab or popup window
            let newTab = window.open("", "_blank");

            fetch(apiUrl)
                .then(response => response.text())
                .then(html => {
                    if (newTab) {
                        newTab.document.open();
                        newTab.document.write(html);
                        newTab.document.close();
                    }
                })
                .catch(error => {
                    alert("Error fetching data: " + error);
                });
        });
        </script>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
</html>