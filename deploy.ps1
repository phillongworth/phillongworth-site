# --- CONFIGURATION ---
$SERVER = "myserver"
$REMOTE_PATH_SITE = "/var/www/phillongworth-site/html"
$REMOTE_PATH_COUK = "/var/www/phillongworth-co-uk/html"
$LOCAL_PATH = "."

Write-Host "--- 🚀 Dual Deployment Started ---" -ForegroundColor Cyan

# --- STEP 0: GENERATE TIMESTAMP ---
# This creates a small file that your website's footer will read
$CurrentTime = Get-Date -Format "dd MMM yyyy, HH:mm:ss"
$VersionJson = '{"timestamp": "' + $CurrentTime + '"}'
if (!(Test-Path "$LOCAL_PATH\data")) { New-Item -ItemType Directory -Path "$LOCAL_PATH\data" }
$VersionJson | Out-File -FilePath "$LOCAL_PATH\data\version.json" -Encoding utf8
Write-Host "Generated version: $CurrentTime" -ForegroundColor Magenta

# --- STEP 1: DEPLOY TO .SITE ---
Write-Host "Step 1: Syncing phillongworth.site..." -ForegroundColor Yellow
# Copying files and recursive folders
& scp -q "$LOCAL_PATH\index.html" "$LOCAL_PATH\style.css" "${SERVER}:${REMOTE_PATH_SITE}"
& scp -q -r "$LOCAL_PATH\assets" "$LOCAL_PATH\data" "$LOCAL_PATH\templates" "${SERVER}:${REMOTE_PATH_SITE}"

# --- STEP 2: DEPLOY TO .CO.UK ---
Write-Host "Step 2: Syncing phillongworth.co.uk..." -ForegroundColor Yellow
# Copying the exact same files to the second domain
& scp -q "$LOCAL_PATH\index.html" "$LOCAL_PATH\style.css" "${SERVER}:${REMOTE_PATH_COUK}"
& scp -q -r "$LOCAL_PATH\assets" "$LOCAL_PATH\data" "$LOCAL_PATH\templates" "${SERVER}:${REMOTE_PATH_COUK}"

# --- STEP 3: THE MAGIC WAND (Permissions) ---
Write-Host "Step 3: Running the Magic Wand on both sites..." -ForegroundColor Yellow
# This fixes ownership, permissions, and reloads Nginx in one go
$MagicCommand = "sudo chown -R www-data:www-data $REMOTE_PATH_SITE $REMOTE_PATH_COUK && " +
               "sudo chmod -R 775 $REMOTE_PATH_SITE $REMOTE_PATH_COUK && " +
               "sudo systemctl reload nginx"

& ssh $SERVER $MagicCommand

Write-Host "--- ✅ Deployment Complete! ---" -ForegroundColor Green
Write-Host "Live at: https://phillongworth.site"
Write-Host "Live at: https://phillongworth.co.uk"