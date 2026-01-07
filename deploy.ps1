Write-Host "--- 🚀 Dual Deployment Started ---" -ForegroundColor Cyan

# --- DEPLOY TO .SITE ---
Write-Host "Step 1: Syncing phillongworth.site..." -ForegroundColor Yellow
& scp -q "$LOCAL_PATH\index.html" "$LOCAL_PATH\style.css" "${SERVER}:${REMOTE_PATH_SITE}"
& scp -q -r "$LOCAL_PATH\assets" "$LOCAL_PATH\data" "$LOCAL_PATH\templates" "${SERVER}:${REMOTE_PATH_SITE}"

# --- DEPLOY TO .CO.UK ---
Write-Host "Step 2: Syncing phillongworth.co.uk..." -ForegroundColor Yellow
& scp -q "$LOCAL_PATH\index.html" "$LOCAL_PATH\style.css" "${SERVER}:${REMOTE_PATH_COUK}"
& scp -q -r "$LOCAL_PATH\assets" "$LOCAL_PATH\data" "$LOCAL_PATH\templates" "${SERVER}:${REMOTE_PATH_COUK}"

# Create a timestamp and save it to the data folder
$CurrentTime = Get-Date -Format "dd MMM yyyy, HH:mm:ss"
$VersionJson = '{"timestamp": "' + $CurrentTime + '"}'
$VersionJson | Out-File -FilePath "$LOCAL_PATH\data\version.json" -Encoding utf8

Write-Host "Generated deployment timestamp: $CurrentTime" -ForegroundColor Magenta
# --- THE DUAL MAGIC WAND ---
Write-Host "Step 3: Running the Magic Wand on both sites..." -ForegroundColor Yellow
& ssh $SERVER "sudo chown -R www-data:www-data $REMOTE_PATH_SITE $REMOTE_PATH_COUK && sudo chmod -R 775 $REMOTE_PATH_SITE $REMOTE_PATH_COUK && sudo systemctl reload nginx"

Write-Host "--- ✅ Both sites are now live! ---" -ForegroundColor Green