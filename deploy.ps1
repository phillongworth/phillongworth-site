$SERVER = "myserver"
$REMOTE_PATH = "/var/www/phillongworth.site/html"
$LOCAL_PATH = ".\"

Write-Host "--- Deployment Started ---" -ForegroundColor Cyan

# 1. Upload files
Write-Host "Step 1: Uploading files to $REMOTE_PATH..." -ForegroundColor Yellow
& scp -q -r "$LOCAL_PATH*" "${SERVER}:${REMOTE_PATH}"

# 2. Fix Permissions & Reload Nginx
Write-Host "Step 2: Refreshing Server permissions and Nginx..." -ForegroundColor Yellow
& ssh $SERVER "sudo chown -R www-data:www-data $REMOTE_PATH && sudo systemctl reload nginx"

Write-Host "--- ✅ Deployment Complete! ---" -ForegroundColor Green