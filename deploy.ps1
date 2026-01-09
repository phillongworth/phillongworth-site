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
& scp -q "$LOCAL_PATH\index.html" "$LOCAL_PATH\*.css" "${SERVER}:${REMOTE_PATH_SITE}"
# Add the js folder to the recursive copy list
& scp -q -r "$LOCAL_PATH\assets" "$LOCAL_PATH\data" "$LOCAL_PATH\templates" "$LOCAL_PATH\js" "${SERVER}:${REMOTE_PATH_SITE}"

# --- STEP 2: DEPLOY TO .CO.UK ---
Write-Host "Step 2: Syncing phillongworth.co.uk..." -ForegroundColor Yellow
& scp -q "$LOCAL_PATH\index.html" "$LOCAL_PATH\*.css" "${SERVER}:${REMOTE_PATH_COUK}"
# Add the js folder here too
& scp -q -r "$LOCAL_PATH\assets" "$LOCAL_PATH\data" "$LOCAL_PATH\templates" "$LOCAL_PATH\js" "${SERVER}:${REMOTE_PATH_COUK}"

$MagicCommand = "chmod -R 775 $REMOTE_PATH_SITE $REMOTE_PATH_COUK && sudo /usr/bin/systemctl reload nginx"

& ssh $SERVER $MagicCommand

Write-Host "--- ✅ Deployment Complete! ---" -ForegroundColor Green
Write-Host "Live at: https://phillongworth.site"
Write-Host "Live at: https://phillongworth.co.uk"