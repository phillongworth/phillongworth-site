$SERVER = "myserver"
$REMOTE_PATH = "/var/www/phillongworth.site/html"
$LOCAL_PATH = "."

Write-Host "--- 🚀 Deployment Started ---" -ForegroundColor Cyan

# 1. Uploading ONLY the web files
Write-Host "Step 1: Syncing index.html..." -ForegroundColor Yellow
& scp -q "$LOCAL_PATH\index.html" "${SERVER}:${REMOTE_PATH}"

# If you have a CSS file, uncomment the line below by removing the '#'
# & scp -q "$LOCAL_PATH\style.css" "${SERVER}:${REMOTE_PATH}"

# 2. Refreshing the server
Write-Host "Step 2: Finalizing on server..." -ForegroundColor Yellow
& ssh $SERVER "sudo chown -R www-data:www-data $REMOTE_PATH && sudo chmod -R 775 $REMOTE_PATH && sudo systemctl reload nginx"

Write-Host "--- ✅ Deployment Complete! ---" -ForegroundColor Green