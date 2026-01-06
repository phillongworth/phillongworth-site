# --- Configuration ---
$SERVER = "myserver"  # This uses the alias we set up in your SSH config
$REMOTE_PATH = "/var/www/phillongworth.site/html" # Update this for each site
$LOCAL_PATH = ".\" # The current folder you are in

Write-Host "🚀 Starting Deployment to $SERVER..." -ForegroundColor Cyan

# 1. Sync files using SCP (Secure Copy)
# This copies everything from your local folder to the server
Write-Host "📦 Uploading files..." -ForegroundColor Yellow
scp -r $LOCAL_PATH/* "${SERVER}:${REMOTE_PATH}"

# 2. Refresh Permissions and Nginx on the Server
Write-Host "🔧 Finalizing on server..." -ForegroundColor Yellow
ssh $SERVER "sudo chown -R www-data:www-data $REMOTE_PATH && sudo systemctl reload nginx"

Write-Host "✅ Deployment Complete! Your site is live." -ForegroundColor Green
