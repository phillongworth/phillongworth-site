$SERVER = "myserver"
$REMOTE_PATH = "/var/www/phillongworth.site/html"
$LOCAL_PATH = ".\"

Write-Host "--- Deployment Started ---" -ForegroundColor Cyan

# 1. Upload ONLY web files (index.html, css, images, etc.)
# Note: We are excluding the .ps1 and .md files for security/cleanliness
Write-Host "Step 1: Uploading web files..." -ForegroundColor Yellow
& scp -q "$LOCAL_PATH\index.html" "${SERVER}:${REMOTE_PATH}"
# If you have a CSS folder or images, add them here:
# & scp -q -r "$LOCAL_PATH\css" "${SERVER}:${REMOTE_PATH}"

# 2. Refresh Permissions and Nginx
Write-Host "Step 2: Refreshing Server..." -ForegroundColor Yellow
& ssh $SERVER "sudo chown -R www-data:www-data $REMOTE_PATH && sudo chmod -R 775 $REMOTE_PATH && sudo systemctl reload nginx"

Write-Host "--- ✅ Deployment Complete! ---" -ForegroundColor Green