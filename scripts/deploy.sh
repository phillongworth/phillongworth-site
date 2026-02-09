#!/bin/bash
# Deploy phillongworth-site
# Run from repository root: ./scripts/deploy.sh [target]
#
# Targets:
#   portfolio  - Deploy static portfolio to remote server via SCP (default)
#   docker     - Deploy all services via Docker Compose
#   docker-portfolio - Deploy only portfolio via Docker
#   docker-bridleway - Deploy bridleway-log with database via Docker

set -e

SERVER="myserver"
REMOTE_PATH="/var/www/phillongworth-site/html"
PORTFOLIO_DIR="apps/portfolio"

deploy_portfolio_scp() {
    echo "Deploying portfolio to ${SERVER}:${REMOTE_PATH}..."

    # HTML and CSS files
    files=(
        "index.html"
        "styles.css"
        "style.css"
        "tools.html"
        "1000-miles-project.html"
        "calderdale-bridleways-project.html"
        "calderdale-climbs-project.html"
        "facey-fifty-project.html"
    )

    # Copy individual HTML/CSS files
    for file in "${files[@]}"; do
        if [ -f "${PORTFOLIO_DIR}/${file}" ]; then
            scp "${PORTFOLIO_DIR}/${file}" "${SERVER}:${REMOTE_PATH}/"
        fi
    done

    # Copy directories
    scp -r "${PORTFOLIO_DIR}/js" "${SERVER}:${REMOTE_PATH}/"
    scp -r "${PORTFOLIO_DIR}/assets" "${SERVER}:${REMOTE_PATH}/"
    scp -r shared "${SERVER}:${REMOTE_PATH}/"
    scp -r data "${SERVER}:${REMOTE_PATH}/"

    echo "Portfolio deployed successfully!"
}

deploy_docker_all() {
    echo "Deploying all services via Docker Compose..."
    docker compose up -d --build
    echo "All services deployed!"
    docker compose ps
}

deploy_docker_portfolio() {
    echo "Deploying portfolio via Docker..."
    docker compose up -d portfolio
    echo "Portfolio deployed!"
    docker compose ps portfolio
}

deploy_docker_bridleway() {
    echo "Deploying bridleway-log via Docker..."
    docker compose up -d bridleway-api db
    echo "Bridleway-log deployed!"
    docker compose ps bridleway-api db
}

# Main
case "${1:-portfolio}" in
    portfolio)
        deploy_portfolio_scp
        ;;
    docker)
        deploy_docker_all
        ;;
    docker-portfolio)
        deploy_docker_portfolio
        ;;
    docker-bridleway)
        deploy_docker_bridleway
        ;;
    *)
        echo "Usage: $0 [portfolio|docker|docker-portfolio|docker-bridleway]"
        exit 1
        ;;
esac
