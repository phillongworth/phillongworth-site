$SERVER = "myserver"
$REMOTE_PATH = "/var/www/phillongworth-site/html"

# Deploy specific web files only (avoids recursive html/ nesting)
$files = @(
    "index.html",
    "styles.css",
    "style.css",
    "script.js",
    "tools.html",
    "1000-miles-project.html",
    "calderdale-bridleways-project.html"
    "calderdale-climbs-project.html",
    "facey-fifty-project.html"
)

# Copy all files + directories in a single scp call (one SSH connection)
$existing = $files | Where-Object { Test-Path $_ }
$allItems = @($existing) + @("data", "assets")
scp -r $allItems "${SERVER}:${REMOTE_PATH}/"
