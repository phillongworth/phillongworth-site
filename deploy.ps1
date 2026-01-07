$SERVER = "myserver"
$REMOTE_PATH = "/var/www/phillongworth-site/html"
$LOCAL_PATH = "."

Write-Host "--- 🚀 Deployment Started ---" -ForegroundColor Cyan

# 1. Uploading everything (HTML, CSS, and all subfolders)
Write-Host "Step 1: Syncing all web files and folders..." -ForegroundColor Yellow

# This copies index.html and style.css
& scp -q "$LOCAL_PATH\index.html" "$LOCAL_PATH\style.css" "${SERVER}:${REMOTE_PATH}"

# This copies your new folders and their contents
& scp -q -r "$LOCAL_PATH\assets" "${SERVER}:${REMOTE_PATH}"
& scp -q -r "$LOCAL_PATH\data" "${SERVER}:${REMOTE_PATH}"
& scp -q -r "$LOCAL_PATH\templates" "${SERVER}:${REMOTE_PATH}"

# 2. Refreshing the server
# Step 2 in your deploy.ps1
& ssh $SERVER "sudo chown -R www-data:www-data /var/www/phillongworth-site/html && sudo chmod -R 775 /var/www/phillongworth-site/html && sudo systemctl reload nginx"

Write-Host "--- ✅ Deployment Complete! ---" -ForegroundColor Green