$SERVER = "myserver"
$REMOTE_PATH = "/var/www/phillongworth.site" # <-- DOUBLE CHECK THIS MATCHES SERVER
$LOCAL_PATH = ".\"
Write-Host "--- Deployment Started ---" -ForegroundColor Cyan

# 1. Upload files
Write-Host "Step 1: Uploading..." -ForegroundColor Yellow
scp -q -r "$LOCAL_PATH*" "${SERVER}:${REMOTE_PATH}"

# 2. Fix Permissions & Reload
Write-Host "Step 2: Refreshing Server..." -ForegroundColor Yellow
ssh $SERVER "sudo chown -R www-data:www-data $REMOTE_PATH && sudo systemctl reload nginx"

Write-Host "--- Deployment Complete! ---" -ForegroundColor Green
