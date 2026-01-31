#!/bin/bash

SERVER="myserver"
REMOTE_PATH="/var/www/phillongworth-site/html"

# Deploy specific web files only (avoids recursive html/ nesting)
files=(
    "index.html"
    "styles.css"
    "style.css"
    "script.js"
    "tools.html"
    "1000-miles-map.html"
    "1000-miles-project.html"
    "calderdale-bridleways-project.html"
    "calderdale-climbs-project.html"
    "facey-fifty-project.html"
)

# Copy individual HTML/CSS/JS files
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        scp "$file" "${SERVER}:${REMOTE_PATH}/"
    fi
done

# Copy data and assets directories
scp -r data "${SERVER}:${REMOTE_PATH}/"
scp -r assets "${SERVER}:${REMOTE_PATH}/"
