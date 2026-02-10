# Deploy phillongworth-site
# Run from repository root: .\scripts\deploy.ps1 [target]
#
# Targets:
#   portfolio  - Deploy static portfolio to remote server via SCP (default)
#   docker     - Deploy all services via Docker Compose
#   docker-portfolio - Deploy only portfolio via Docker
#   docker-bridleway - Deploy bridleway-log with database via Docker

param(
    [string]$Target = "portfolio"
)

$SERVER = "myserver"
$REMOTE_PATH = "/var/www/phillongworth-site/html"
$PORTFOLIO_DIR = "apps/portfolio"

function Deploy-PortfolioScp {
    Write-Host "Deploying portfolio to ${SERVER}:${REMOTE_PATH}..." -ForegroundColor Cyan

    $files = @(
        "index.html",
        "styles.css",
        "style.css",
        "tools.html",
        "1000-miles-project.html",
        "calderdale-bridleways-project.html",
        "calderdale-climbs-project.html",
        "facey-fifty-project.html"
    )

    # Build list of existing files with full paths
    $existing = $files | ForEach-Object { "$PORTFOLIO_DIR/$_" } | Where-Object { Test-Path $_ }

    # Add directories
    $allItems = @($existing) + @(
        "$PORTFOLIO_DIR/js",
        "$PORTFOLIO_DIR/assets",
        "shared",
        "data"
    )

    # Copy all in a single SCP call
    scp -r $allItems "${SERVER}:${REMOTE_PATH}/"

    Write-Host "Portfolio deployed successfully!" -ForegroundColor Green
}

function Deploy-DockerAll {
    Write-Host "Deploying all services via Docker Compose..." -ForegroundColor Cyan
    docker compose up -d --build
    Write-Host "All services deployed!" -ForegroundColor Green
    docker compose ps
}

function Deploy-DockerPortfolio {
    Write-Host "Deploying portfolio via Docker..." -ForegroundColor Cyan
    docker compose up -d portfolio
    Write-Host "Portfolio deployed!" -ForegroundColor Green
    docker compose ps portfolio
}

function Deploy-DockerBridleway {
    Write-Host "Deploying bridleway-log via Docker..." -ForegroundColor Cyan
    docker compose up -d bridleway-api db
    Write-Host "Bridleway-log deployed!" -ForegroundColor Green
    docker compose ps bridleway-api db
}

# Main
switch ($Target) {
    "portfolio" { Deploy-PortfolioScp }
    "docker" { Deploy-DockerAll }
    "docker-portfolio" { Deploy-DockerPortfolio }
    "docker-bridleway" { Deploy-DockerBridleway }
    default {
        Write-Host "Usage: .\deploy.ps1 [portfolio|docker|docker-portfolio|docker-bridleway]" -ForegroundColor Yellow
        exit 1
    }
}
