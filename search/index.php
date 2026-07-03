<?php
session_start();

// Use a more robust inclusion method
require_once('../scripts/php/config.php');
require_once('../scripts/php/functions.php');

/**
 * Search Interface Refactor
 * 
 * Changes:
 * 1. Switched from mysqli query to PDO prepared statements for security.
 * 2. Improved HTML output generation using a template-like approach.
 * 3. Added basic error handling to prevent leaking system internals.
 */

try {
    // Use the PDO object defined in config.php
    // We limit the result set for performance and use a prepared statement
    $stmt = $pdo->prepare("SELECT id, title, description, type_topic, keywords, url, url_hash, image_url FROM `index` ORDER BY id DESC LIMIT 500");
    $stmt->execute();

    $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    $html_output_latest = "";

    foreach ($results as $row) {
        // Sanitize all output to prevent XSS
        $title = htmlspecialchars($row['title'] ?? 'No Title', ENT_QUOTES, 'UTF-8');
        $description = htmlspecialchars($row['description'] ?? '', ENT_QUOTES, 'UTF-8');
        $url = htmlspecialchars($row['url'] ?? '#', ENT_QUOTES, 'UTF-8');
        
        $html_output_latest .= <<<HTML
        <div class="card mb-3" style="max-width: 540px;">
            <div class="row g-0">
                <div class="col-lg-4">
                    <img src="{$row['image_url']}" class="img-fluid rounded-start" alt="Thumbnail" onerror="this.src='https://via.placeholder.com/150'">
                </div>
                <div class="col-lg-8">
                    <div class="card-body">
                        <h5 class="card-title text-wrap truncate">
                            <a href="{$url}" target="_blank" rel="noopener noreferrer">{$title}</a>
                        </h5>
                        <p class="card-text text-muted small">{$description}</p>
                        <p class="card-text"><small class="text-muted">Indexed via AdaptEngine</small></p>
                    </div>
                </div>
            </div>
        </div>
HTML;
    }
} catch (\PDOException $e) {
    // Log the error internally, show a friendly message to the user
    error_log("Database Error: " . $e->getMessage());
    die("A technical error occurred. Please try again later.");
} catch (\Throwable $th) {
    error_log("General Error: " . $th->getMessage());
    die("An unexpected error occurred.");
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AdaptEngine&trade;_ZA | Curated Research Engine &copy; <?php echo date('Y'); ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .truncate {
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg fixed-top navbar-dark bg-dark p-4 shadow">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">AdaptEngine&trade;_ZA | Curated Research Engine</a>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#">Sign In</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <nav class="navbar navbar-expand-lg fixed-bottom bg-light p-4 shadow-sm text-end">
        <div class="container-fluid">
            <p class="m-0 text-muted small">Crafted by AdaptivConcept &copy; <?php echo date('Y'); ?></p>
        </div>
    </nav>

    <div class="container-fluid" style="padding-top: 120px; padding-bottom: 100px;">
        <div class="row">
            <div class="col-md-8">
                <!-- Search Content can go here -->
                <div class="alert alert-info">Welcome to the research index. The latest crawled pages are listed to the right.</div>
            </div>
            <div class="col-md-4">
                <h3 class="mb-4">Latest Index</h3>
                <?php echo $html_output_latest ?: '<p class="text-muted">No pages indexed yet.</p>'; ?>
            </div>
        </div>
    </div>
</body>
</html>
