$SERVER = "myserver"
$REMOTE_PATH = "/var/www/phillongworth-site/html"
$LOCAL_PATH = "."

Write-Host "--- 🚀 Deployment Started ---" -ForegroundColor Cyan

# 1. Clear old file and upload new one
Write-Host "Step 1: Syncing index.html..." -ForegroundColor Yellow
& ssh $SERVER "rm -f $REMOTE_PATH/index.html"  # Force delete old file first
& scp -q "$LOCAL_PATH\index.html" "${SERVER}:${REMOTE_PATH}"

# If you have a CSS file, uncomment the line below by removing the '#'
# & scp -q "$LOCAL_PATH\style.css" "${SERVER}:${REMOTE_PATH}"

# 2. Refreshing the server
# Step 2 in your deploy.ps1
& ssh $SERVER "sudo chown -R www-data:www-data /var/www/phillongworth-site/html && sudo chmod -R 775 /var/www/phillongworth-site/html && sudo systemctl reload nginx"

Write-Host "--- ✅ Deployment Complete! ---" -ForegroundColor Green