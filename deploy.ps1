$SERVER = "myserver"
$REMOTE_PATH = "/var/www/phillongworth.site/html"
$LOCAL_PATH = ".\"

Write-Host "--- 🚀 Deployment Started ---" -ForegroundColor Cyan

# 1. Uploading only web-relevant files
# 1. Uploading only web-relevant files
Write-Host "Step 1: Syncing index.html..." -ForegroundColor Yellow
& scp -q "$LOCAL_PATH\index.html" "${SERVER}:${REMOTE_PATH}"

# If you have other folders like 'css' or 'assets', add them like this:
# & scp -q -r "$LOCAL_PATH\css" "${SERVER}:${REMOTE_PATH}"
  --exclude="*.ps1" --exclude="*.md" --exclude=".git"

# 2. Refreshing the server
Write-Host "Step 2: Finalizing on server..." -ForegroundColor Yellow
& ssh $SERVER "sudo chown -R www-data:www-data $REMOTE_PATH && sudo chmod -R 775 $REMOTE_PATH && sudo systemctl reload nginx"

Write-Host "--- ✅ Deployment Complete! Site is live at https://phillongworth.site ---" -ForegroundColor Green