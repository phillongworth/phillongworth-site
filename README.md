# phillongworth-site

Monorepo for [phillongworth.site](https://phillongworth.site) containing the portfolio website and bridleway tracking application.

## Structure

```
phillongworth-site/
├── apps/
│   ├── portfolio/          # Static portfolio website
│   │   ├── index.html      # Homepage
│   │   ├── *-project.html  # Project pages (1000 Miles, Climbs, etc.)
│   │   ├── style.css       # Homepage styles
│   │   ├── styles.css      # Project page styles
│   │   ├── js/             # JavaScript
│   │   └── assets/         # Images
│   │
│   └── bridleway-log/      # Full-stack bridleway tracking app
│       ├── backend/        # FastAPI Python backend
│       ├── frontend/       # Vanilla JS + Leaflet frontend
│       └── docker-compose.yml  # App-specific compose (legacy)
│
├── shared/
│   ├── css/base.css        # Common styles (reset, typography, footer)
│   ├── js/leaflet-config.js # Shared Leaflet map configuration
│   └── python/geo_utils.py # Shared geo utilities (haversine, etc.)
│
├── data/
│   ├── gpx/                # GPX track files
│   │   ├── 1000-miles/     # 1000 Miles project routes
│   │   └── climbs/         # Climb GPX files
│   ├── generated/          # Build outputs (tracks.json, etc.)
│   └── spreadsheets/       # Excel data files
│
├── scripts/
│   ├── build_*.py          # Data build scripts
│   ├── deploy.sh           # Bash deployment script
│   └── deploy.ps1          # PowerShell deployment script
│
├── docker-compose.yml      # Unified deployment
└── .env.example            # Environment template
```

## Quick Start

### Portfolio (Static Site)

```bash
# Local development - open in browser
open apps/portfolio/index.html

# Deploy to remote server
./scripts/deploy.sh portfolio
```

### Bridleway Log (Full Stack)

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with secure passwords

# Start with Docker
docker compose up -d bridleway-api db

# Access at http://localhost:6080
```

### All Services

```bash
docker compose up -d
# Portfolio: http://localhost:80
# Bridleway Log: http://localhost:6080
```

## Build Scripts

```bash
# Build 1000 Miles track data
python scripts/build_map_data.py

# Build Calderdale 50 climb data
python scripts/build_calderdale_data.py

# Build Facey Fifty climb data
python scripts/build_facey_data.py
```

## Deployment Options

| Command | Description |
|---------|-------------|
| `./scripts/deploy.sh portfolio` | Deploy portfolio via SCP |
| `./scripts/deploy.sh docker` | Deploy all via Docker |
| `./scripts/deploy.sh docker-portfolio` | Deploy portfolio via Docker |
| `./scripts/deploy.sh docker-bridleway` | Deploy bridleway-log via Docker |

## Technology Stack

- **Portfolio**: HTML, CSS, Leaflet.js
- **Bridleway Log**: FastAPI, PostgreSQL/PostGIS, Leaflet.js
- **Deployment**: Docker Compose, Nginx, Cloudflare Tunnel
