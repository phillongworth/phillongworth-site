# Phil Longworth Digital - Complete User Guide

**Last Updated:** January 2026
**Server:** `optiplex7040-server`
**User:** `phil`

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Domains & Routing](#domains--routing)
3. [phillongworth.site (Static Site)](#phillongworthsite-static-site)
4. [Bridleway Log (Web Application)](#bridleway-log-web-application)
5. [phillongworth.co.uk (Portfolio Site)](#phillongworthcouk-portfolio-site)
6. [VS Code Setup](#vs-code-setup)
7. [Git Workflow](#git-workflow)
8. [Deploying Changes](#deploying-changes)
9. [Server Administration](#server-administration)
10. [Adding New Sites & Apps](#adding-new-sites--apps)
11. [Backup & Recovery](#backup--recovery)
12. [Troubleshooting](#troubleshooting)
13. [Quick Reference](#quick-reference)

---

## Architecture Overview

All sites are served through a **Cloudflare Tunnel** — no ports are open to the internet.

```
Internet --> Cloudflare Edge --> Tunnel --> Local Nginx (port 80)
                                               |
                    +--------------------------+--------------------------+
                    |                          |                          |
           phillongworth.site         map.phillongworth.site     phillongworth.co.uk
             |           |                     |                         |
         Static HTML   /bridleway/        /bridleway/               Static HTML
         (nginx)       (proxy)            (proxy)                   (nginx)
                          |                    |
                          +-----> Docker container (FastAPI + PostGIS)
                                  localhost:6080
```

### Key Benefits

- No open ports (80/443 closed to the internet)
- Cloudflare handles SSL certificates automatically
- DDoS protection included
- No need for Let's Encrypt/Certbot

### Technology Stack

| Component | Technology |
|-----------|-----------|
| Web server | Nginx 1.24 |
| Tunnel | Cloudflare (`cloudflared`) |
| Static sites | HTML, CSS, JavaScript, Leaflet |
| Bridleway Log backend | Python 3.12, FastAPI, SQLAlchemy, GeoAlchemy2 |
| Bridleway Log database | PostgreSQL 16 + PostGIS |
| Containers | Docker Compose |
| Source control | Git + GitHub |
| Development | VS Code on Windows |

---

## Domains & Routing

| URL | Content | Served By |
|-----|---------|-----------|
| `phillongworth.site` | Cycling projects static site | Nginx -> `/var/www/phillongworth-site/html` |
| `phillongworth.site/bridleway/` | Bridleway Log app | Nginx proxy -> Docker `localhost:6080` |
| `map.phillongworth.site/bridleway/` | Bridleway Log app (alias) | Nginx proxy -> Docker `localhost:6080` |
| `phillongworth.co.uk` | Professional portfolio | Nginx -> `/var/www/phillongworth-co-uk` |

### Nginx Configuration Files

| File | Domain |
|------|--------|
| `/etc/nginx/sites-available/phillongworth.site` | phillongworth.site + /bridleway/ proxy |
| `/etc/nginx/sites-available/map.phillongworth.site` | map.phillongworth.site (bridleway alias) |
| `/etc/nginx/sites-available/phillongworth.co.uk` | phillongworth.co.uk |
| `/etc/nginx/sites-enabled/` | Symlinks to enabled configs |

### Cloudflare Tunnel

**Tunnel ID:** `12a6f249-55ad-4062-857f-6cbbce47f429`
**Tunnel Name:** `phillongworth-co-uk`

```yaml
# /etc/cloudflared/config.yml
tunnel: 12a6f249-55ad-4062-857f-6cbbce47f429
credentials-file: /etc/cloudflared/12a6f249-55ad-4062-857f-6cbbce47f429.json

ingress:
  - hostname: phillongworth.co.uk
    service: http://localhost:80
  - hostname: www.phillongworth.co.uk
    service: http://localhost:80
  - hostname: phillongworth.site
    service: http://localhost:80
  - hostname: www.phillongworth.site
    service: http://localhost:80
  - hostname: map.phillongworth.site
    service: http://localhost:80
  - service: http_status:404
```

---

## phillongworth.site (Static Site)

A static website showcasing cycling challenge tracking and projects with interactive maps.

### GitHub Repository

`git@github.com:phillongworth/phillongworth-site.git`

### Directory Structure

```
/var/www/phillongworth-site/           <-- Git repository root
├── index.html                         <-- Homepage (source)
├── style.css                          <-- Homepage stylesheet
├── styles.css                         <-- Project pages stylesheet
├── 1000-miles-map.html
├── 1000-miles-project.html
├── calderdale-bridleways-project.html
├── calderdale-climbs-project.html
├── facey-fifty-project.html
├── tools.html
├── js/
│   └── script.js
├── assets/
│   └── images/                        <-- Project images
├── data/
│   ├── 1001.gpx - 1072.gpx           <-- 1000 Miles GPX tracks
│   ├── Calderdale50gpx/               <-- Calderdale 50 climb GPX files
│   ├── tracks.json                    <-- Generated map data
│   ├── calderdale50.json              <-- Generated climb data
│   ├── facey_fifty.json               <-- Generated climb data
│   └── *.xlsx                         <-- Progress spreadsheets
├── build_map_data.py                  <-- Generates tracks.json
├── build_calderdale_data.py           <-- Generates calderdale50.json
├── build_facey_data.py                <-- Generates facey_fifty.json
├── scrape_calderdale50.py             <-- Scrapes climb data
├── scrape_facey_fifty.py              <-- Scrapes climb data
├── fetch_strava_segments.py           <-- Fetches Strava data
├── deploy.sh                          <-- SCP deployment script
├── deploy.ps1                         <-- PowerShell deployment script
├── html/                              <-- Nginx web root (deployment copy, gitignored)
├── to_delete/                         <-- Files pending deletion (gitignored)
├── .gitignore
├── README.md
└── SERVER_MANUAL.md
```

### Key Project Pages

| File | Purpose |
|------|---------|
| `index.html` | Homepage with links to all projects |
| `1000-miles-map.html` | Interactive map showing all 1000 Miles routes |
| `1000-miles-project.html` | 1000 Miles project description |
| `calderdale-climbs-project.html` | Calderdale 50 climbs with map |
| `calderdale-bridleways-project.html` | Calderdale bridleways project |
| `facey-fifty-project.html` | Facey Fifty climbs with map |
| `tools.html` | Cycling/mapping tools page |

### How Deployment Works

Source files live at the repository root. The `html/` directory is the nginx web root and contains a copy of the served files. The `html/` directory is gitignored.

**To deploy changes after editing source files:**

```bash
# On the server
cd /var/www/phillongworth-site
git pull

# Copy source files to the nginx web root
cp index.html styles.css style.css tools.html html/
cp 1000-miles-map.html 1000-miles-project.html html/
cp calderdale-bridleways-project.html calderdale-climbs-project.html html/
cp facey-fifty-project.html html/
cp -r data/* html/data/
cp -r assets/* html/assets/
cp -r js/* html/js/
```

Or use the deploy script from Windows:
```powershell
.\deploy.ps1
```

### Building Data Files

The JSON data files used by the map pages are generated from GPX files by Python scripts:

```bash
# Generate tracks.json from numbered GPX files
python build_map_data.py

# Generate calderdale50.json
python build_calderdale_data.py

# Generate facey_fifty.json
python build_facey_data.py
```

After regenerating data, copy updated files to `html/data/`.

---

## Bridleway Log (Web Application)

A full-stack web application for viewing public rights of way on an interactive map with GPX upload and ridden coverage tracking.

### GitHub Repository

`git@github.com:phillongworth/bridleway-log.git`

### Access URLs

- `https://phillongworth.site/bridleway/`
- `https://map.phillongworth.site/bridleway/`

### Directory Structure

```
/var/www/bridleway-log/
├── backend/
│   ├── app/
│   │   ├── main.py              <-- FastAPI entry point
│   │   ├── config.py            <-- Database URL config
│   │   ├── db.py                <-- SQLAlchemy session
│   │   ├── models.py            <-- Path and Ride models (PostGIS)
│   │   ├── schemas.py           <-- Pydantic request/response schemas
│   │   ├── api/
│   │   │   ├── paths.py         <-- /api/paths, /api/path-types
│   │   │   ├── stats.py         <-- /api/stats, /api/areas
│   │   │   ├── rides.py         <-- /api/rides, /api/rides/upload
│   │   │   └── bridleways.py    <-- /api/bridleways/upload
│   │   └── services/
│   │       └── coverage.py      <-- Coverage calculation (PostGIS spatial ops)
│   ├── scripts/
│   │   ├── import_paths.py      <-- Import GeoJSON path data
│   │   ├── import_gpx.py        <-- Batch import GPX ride files
│   │   └── migrate.py           <-- Database migration script
│   ├── migrations/
│   │   └── 002_add_rides_and_coverage.sql
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html               <-- Single-page app
│   └── assets/
│       ├── js/main.js           <-- All frontend logic
│       └── css/styles.css       <-- All styling
├── data/                        <-- Mounted into Docker container at /data
├── docker-compose.yml
├── .env / .env.example
├── .gitignore
├── README.md
└── CLAUDE.md
```

### Docker Services

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| `web` | bridleway-log-web-1 | 6080 -> 8000 | FastAPI backend + static frontend |
| `db` | bridleway-log-db-1 | 5432 (internal) | PostgreSQL 16 + PostGIS |

### Common Docker Commands

```bash
cd /var/www/bridleway-log

# Start the application
docker compose up -d

# Stop the application
docker compose down

# Rebuild after backend code changes
docker compose build web && docker compose up -d

# View application logs
docker compose logs -f web

# Run database migration
docker compose run --rm web python scripts/migrate.py

# Access PostgreSQL directly
docker compose exec db psql -U bridleway -d bridleway_log
```

### Importing Path Data

```bash
# Import GeoJSON data for an area
docker compose run --rm web python scripts/import_paths.py \
    --file /data/Calderdale-JSON.json \
    --area "CMBC RoW Network"

# Replace existing data for an area (--clear)
docker compose run --rm web python scripts/import_paths.py \
    --file /data/filename.json --area "Area Name" --clear
```

### GeoJSON Import Format

The import script expects features with these properties:

| GeoJSON Property | Database Column | Description |
|-----------------|-----------------|-------------|
| `fid` | `source_fid` | Feature ID |
| `RouteCode` | `route_code` | Route code |
| `Name` | `name` | Path name |
| `StatusDesc` | `path_type` | Footpath, Bridleway, Restricted Byway, BOAT |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/paths?area=&path_type=&ridden=&min_coverage=` | GET | Paths as GeoJSON with coverage data |
| `/api/stats` | GET | Path counts, lengths, coverage statistics |
| `/api/areas` | GET | List of area names |
| `/api/path-types` | GET | List of path types |
| `/api/rides` | GET | List of uploaded rides |
| `/api/rides/upload` | POST | Upload GPX files (multipart form) |
| `/api/rides/geojson` | GET | All rides as GeoJSON |
| `/api/rides/{id}` | DELETE | Delete a ride and recompute coverage |
| `/api/coverage/recompute` | POST | Manually recalculate coverage |
| `/api/bridleways/upload` | POST | Upload GeoJSON bridleway data |
| `/api/bridleways/area/{name}` | DELETE | Delete area data |

### GPX Upload & Coverage Calculation

Upload GPX files through the sidebar in the web UI. Coverage is automatically recalculated after upload.

**How coverage works:**
- A path is "ridden" if at least **80%** of its length is within **30 metres** of any uploaded GPX track
- Uses PostGIS spatial operations (buffer, intersection, length comparison)
- Parameters in `backend/app/services/coverage.py`:
  - `COVERAGE_MIN_FRACTION = 0.8`
  - `COVERAGE_BUFFER_METERS = 30`

### Database Models

**Path** (`paths` table): `id`, `source_fid`, `route_code`, `name`, `path_type`, `area`, `geometry` (LINESTRING), `length_km`, `is_ridden`, `coverage_fraction`, `last_ridden_date`

**Ride** (`rides` table): `id`, `filename`, `file_hash` (SHA-256 dedup), `date_recorded`, `distance_km`, `elevation_gain_m`, `geometry` (MULTILINESTRING), `created_at`

---

## phillongworth.co.uk (Portfolio Site)

A professional portfolio/resume site.

### GitHub Repository

`git@github.com:phillongworth/phillongworth-co-uk.git`

### Directory Structure

```
/var/www/phillongworth-co-uk/
├── index.html           <-- Served directly by nginx
├── assets/
└── .git/
```

**Note:** Unlike phillongworth-site, this project serves files directly from the repository root (no `html/` subdirectory).

---

## VS Code Setup

### Recommended Extensions

| Extension | Purpose |
|-----------|---------|
| **Live Server** | Preview changes locally before deploying |
| **HTML CSS Support** | Autocomplete for HTML/CSS |
| **Prettier** | Auto-format code on save |
| **GitLens** | Enhanced Git integration |
| **Remote - SSH** | Edit files directly on server (optional) |

### Opening Projects

```powershell
# phillongworth.site
cd C:\Users\phill\OneDrive\Documents\GitHub\phillongworth-site
code .

# bridleway-log
cd C:\Users\phill\OneDrive\Documents\GitHub\bridleway-log
code .

# phillongworth.co.uk
cd C:\Users\phill\OneDrive\Documents\GitHub\phillongworth-co-uk
code .
```

### Live Preview (Local Testing)

1. Install the **Live Server** extension
2. Right-click on `index.html` (or `html/index.html`)
3. Select **Open with Live Server**
4. Browser opens at `http://127.0.0.1:5500`
5. Changes auto-refresh in the browser

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open Source Control | `Ctrl+Shift+G` |
| Open Terminal | `` Ctrl+` `` |
| Save File | `Ctrl+S` |
| Save All | `Ctrl+K S` |

---

## Git Workflow

### Initial Clone (One-Time Setup)

```powershell
cd C:\Users\phill\OneDrive\Documents\GitHub

git clone git@github.com:phillongworth/phillongworth-site.git
git clone git@github.com:phillongworth/bridleway-log.git
git clone git@github.com:phillongworth/phillongworth-co-uk.git
```

### Daily Workflow

#### 1. Pull Latest Changes

Always pull before making changes to avoid conflicts:

```powershell
git pull
```

#### 2. Make Your Edits

Edit files in VS Code.

#### 3. Check What Changed

```powershell
git status        # See modified files
git diff          # See actual changes
```

#### 4. Stage, Commit, Push

```powershell
git add index.html style.css        # Stage specific files
git commit -m "Update homepage"     # Commit with message
git push                            # Push to GitHub
```

Or using VS Code's sidebar:

1. Click **Source Control** icon (branch symbol)
2. Click **+** to stage files
3. Type commit message
4. Click checkmark to commit
5. Click **...** -> **Push**

#### 5. Deploy to Server

See [Deploying Changes](#deploying-changes) below.

### Commit Message Guidelines

Write meaningful messages describing what changed:
- "Add new GPX route 1073"
- "Fix map zoom level on mobile"
- "Update bridleway upload error handling"

---

## Deploying Changes

### phillongworth.site

```bash
# On server
cd /var/www/phillongworth-site
git pull

# Copy to nginx web root
cp index.html styles.css style.css tools.html html/
cp 1000-miles-map.html 1000-miles-project.html html/
cp calderdale-bridleways-project.html calderdale-climbs-project.html html/
cp facey-fifty-project.html html/
cp -r data/* html/data/
cp -r assets/* html/assets/
cp -r js/* html/js/
```

Or from Windows:
```powershell
git push && ssh myserver "cd /var/www/phillongworth-site && git pull"
```

### Bridleway Log

```bash
cd /var/www/bridleway-log
git pull

# If backend code changed, rebuild the container
docker compose build web && docker compose up -d

# If only frontend changed, no rebuild needed (files are mounted read-only)

# If database schema changed
docker compose run --rm web python scripts/migrate.py
```

### phillongworth.co.uk

```bash
# On server
cd /var/www/phillongworth-co-uk
git pull
```

Files are served directly from the repository root, so pulling is all that's needed.

### One-Line Deploy from Windows

```powershell
# phillongworth.site
git push && ssh myserver "cd /var/www/phillongworth-site && git pull"

# bridleway-log (frontend only)
git push && ssh myserver "cd /var/www/bridleway-log && git pull"

# bridleway-log (backend changes)
git push && ssh myserver "cd /var/www/bridleway-log && git pull && docker compose build web && docker compose up -d"

# phillongworth.co.uk
git push && ssh myserver "cd /var/www/phillongworth-co-uk && git pull"
```

---

## Server Administration

### Check Service Status

```bash
# Cloudflare Tunnel
sudo systemctl status cloudflared

# Nginx
sudo systemctl status nginx

# Bridleway Log Docker containers
docker ps

# All services at once
sudo systemctl status cloudflared nginx && docker ps
```

### Restart Services

```bash
# After changing tunnel config
sudo systemctl restart cloudflared

# After changing nginx config
sudo nginx -t && sudo systemctl reload nginx

# Restart Bridleway Log
cd /var/www/bridleway-log && docker compose restart

# Rebuild and restart Bridleway Log
cd /var/www/bridleway-log && docker compose build web && docker compose up -d
```

### View Logs

```bash
# Tunnel logs
journalctl -u cloudflared -f

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log

# Bridleway Log application logs
docker compose -f /var/www/bridleway-log/docker-compose.yml logs -f web

# Bridleway Log database logs
docker compose -f /var/www/bridleway-log/docker-compose.yml logs -f db
```

### Tunnel Management

```bash
cloudflared tunnel list
cloudflared tunnel info phillongworth-co-uk
```

---

## Adding New Sites & Apps

### Adding a New Map App to map.phillongworth.site

1. Deploy your app (e.g., on port 6090)

2. Edit the nginx config:
   ```bash
   sudo nano /etc/nginx/sites-available/map.phillongworth.site
   ```

   Add a new location block:
   ```nginx
   location /newmap/ {
       proxy_pass http://localhost:6090/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_redirect / /newmap/;
   }

   location /newmap {
       return 301 /newmap/;
   }
   ```

3. Reload nginx:
   ```bash
   sudo nginx -t && sudo systemctl reload nginx
   ```

4. Access at: `https://map.phillongworth.site/newmap/`

### Adding a New Domain

1. Add the domain to Cloudflare (if not already there)

2. Add a CNAME record in Cloudflare DNS:
   - Type: `CNAME`
   - Name: `@` (or subdomain)
   - Target: `12a6f249-55ad-4062-857f-6cbbce47f429.cfargotunnel.com`
   - Proxy: Enabled (orange cloud)

3. Update tunnel config:
   ```bash
   sudo nano /etc/cloudflared/config.yml
   ```
   Add before the catch-all:
   ```yaml
     - hostname: newdomain.com
       service: http://localhost:80
   ```

4. Create nginx config:
   ```bash
   sudo nano /etc/nginx/sites-available/newdomain.com
   ```
   ```nginx
   server {
       listen 80;
       listen [::]:80;
       server_name newdomain.com www.newdomain.com;

       root /var/www/newdomain/html;
       index index.html;

       location / {
           try_files $uri $uri/ =404;
       }
   }
   ```

5. Enable and restart:
   ```bash
   sudo ln -s /etc/nginx/sites-available/newdomain.com /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   sudo systemctl restart cloudflared
   ```

---

## Backup & Recovery

### Backup Web Content

```bash
tar -cvzf ~/backup_$(date +%F).tar.gz /var/www/
```

### Backup Tunnel Credentials

```bash
cp /etc/cloudflared/*.json ~/cloudflared-backup/
cp /etc/cloudflared/config.yml ~/cloudflared-backup/
```

### Backup Bridleway Log Database

```bash
docker compose -f /var/www/bridleway-log/docker-compose.yml exec db \
    pg_dump -U bridleway bridleway_log > ~/bridleway-backup_$(date +%F).sql
```

### Restore Database from Backup

```bash
docker compose -f /var/www/bridleway-log/docker-compose.yml exec -T db \
    psql -U bridleway bridleway_log < ~/bridleway-backup_2026-01-31.sql
```

### Restore Web Content from Backup

```bash
sudo tar -xzf ~/backup_2026-01-31.tar.gz -C /
```

---

## Troubleshooting

### Site Not Loading at All

1. **Check the tunnel:**
   ```bash
   sudo systemctl status cloudflared
   cloudflared tunnel info phillongworth-co-uk
   ```
   Should show 4 connections to Cloudflare edge.

2. **Check nginx:**
   ```bash
   sudo systemctl status nginx
   ```

3. **Test locally on the server:**
   ```bash
   curl -I http://localhost -H "Host: phillongworth.site"
   curl -I http://localhost -H "Host: phillongworth.co.uk"
   curl -I http://localhost/bridleway/ -H "Host: phillongworth.site"
   ```

### 502 Bad Gateway

The backend service isn't responding.

```bash
# Check nginx is running
sudo systemctl status nginx

# For bridleway app, check Docker container is running
docker ps | grep bridleway

# If container is down, restart it
cd /var/www/bridleway-log && docker compose up -d
```

### 404 Not Found

1. **Static site:** Check that files exist in the correct directory:
   ```bash
   ls /var/www/phillongworth-site/html/index.html
   ls /var/www/phillongworth-co-uk/index.html
   ```

2. **Bridleway app:** Check the container is running and nginx proxy is configured:
   ```bash
   docker ps | grep bridleway
   curl http://localhost:6080/
   ```

### Changes Not Showing on Live Site

1. **Hard refresh in browser:** `Ctrl+Shift+R`
2. **Check deployment:** Did you pull on the server?
3. **For phillongworth.site:** Did you copy files to `html/`?
   ```bash
   ls -la /var/www/phillongworth-site/html/
   ```
4. **For bridleway-log frontend:** Files are mounted read-only, so a `git pull` is enough. But if backend changed, you need to rebuild:
   ```bash
   cd /var/www/bridleway-log
   docker compose build web && docker compose up -d
   ```

### Bridleway Log: Container Won't Start

```bash
cd /var/www/bridleway-log

# Check logs for errors
docker compose logs web
docker compose logs db

# Common fix: rebuild the image
docker compose build web && docker compose up -d

# If database is corrupted, reset (WARNING: deletes all data)
docker compose down -v && docker compose up -d
```

### Bridleway Log: GPX Upload Fails

1. Check the web container logs:
   ```bash
   docker compose -f /var/www/bridleway-log/docker-compose.yml logs -f web
   ```
2. Ensure the `/data` volume mount exists:
   ```bash
   ls /var/www/bridleway-log/data/
   ```
3. Check file format — must be valid `.gpx` files

### Bridleway Log: Coverage Not Updating

Manually trigger a recompute:
```bash
curl -X POST http://localhost:6080/api/coverage/recompute
```

### Tunnel Won't Start

1. Check config syntax:
   ```bash
   cat /etc/cloudflared/config.yml
   ```
   - YAML is space-sensitive — no tabs
   - Top-level keys must not be indented

2. Check logs:
   ```bash
   journalctl -u cloudflared -n 50
   ```

3. Common errors:
   - `yaml: line X: mapping values are not allowed` = indentation problem
   - `no such file or directory` = credentials file missing

### DNS Not Resolving

1. Check Cloudflare DNS panel — ensure CNAME records exist and are proxied (orange cloud)

2. Test DNS resolution:
   ```bash
   dig phillongworth.site @1.1.1.1 +short
   ```
   Should return Cloudflare IPs (104.x.x.x or 172.x.x.x)

3. DNS propagation may take a few minutes after adding records

### Nginx Config Errors

```bash
# Test configuration syntax
sudo nginx -t

# View specific error details
sudo nginx -t 2>&1
```

Common fixes:
- Missing semicolon at end of line
- Broken symlink in `sites-enabled/`
- Duplicate `server_name` across configs

### "Permission denied" When Pushing to GitHub

SSH key isn't set up:

```powershell
# Check if key exists
cat ~/.ssh/id_ed25519.pub

# If not, generate one
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy public key and add to GitHub -> Settings -> SSH Keys
cat ~/.ssh/id_ed25519.pub
```

### Git Says "Divergent Branches"

Your local and remote have different commits:

```powershell
# Option 1: Rebase local on top of remote
git pull --rebase

# Option 2: Force local to match remote (loses local changes!)
git fetch origin
git reset --hard origin/main
```

### Server Files Differ from GitHub

Reset server to match GitHub exactly:

```bash
cd /var/www/phillongworth-site   # or bridleway-log, phillongworth-co-uk
git fetch origin
git reset --hard origin/main
```

### VS Code Not Recognizing Git

Open the correct folder — the one containing `.git`:
- Open `phillongworth-site`, not `phillongworth-site/html`
- Open `bridleway-log`, not `bridleway-log/backend`

---

## Quick Reference

### Service Commands

| Task | Command |
|------|---------|
| Check tunnel | `sudo systemctl status cloudflared` |
| Restart tunnel | `sudo systemctl restart cloudflared` |
| Check nginx | `sudo systemctl status nginx` |
| Reload nginx | `sudo nginx -t && sudo systemctl reload nginx` |
| Check Docker | `docker ps` |
| View tunnel logs | `journalctl -u cloudflared -f` |
| View nginx logs | `tail -f /var/log/nginx/error.log` |
| View app logs | `docker compose -f /var/www/bridleway-log/docker-compose.yml logs -f web` |
| Test site locally | `curl -I http://localhost -H "Host: phillongworth.site"` |

### Git Commands

| Task | Command |
|------|---------|
| Check status | `git status` |
| Pull changes | `git pull` |
| Stage all | `git add .` |
| Commit | `git commit -m "message"` |
| Push | `git push` |
| View history | `git log --oneline -10` |
| Undo local changes | `git checkout -- filename` |
| Discard all changes | `git reset --hard HEAD` |

### Deployment One-Liners (from Windows)

```powershell
# phillongworth.site
git push && ssh myserver "cd /var/www/phillongworth-site && git pull"

# bridleway-log (frontend only)
git push && ssh myserver "cd /var/www/bridleway-log && git pull"

# bridleway-log (backend changes)
git push && ssh myserver "cd /var/www/bridleway-log && git pull && docker compose build web && docker compose up -d"

# phillongworth.co.uk
git push && ssh myserver "cd /var/www/phillongworth-co-uk && git pull"
```

### Useful Links

- **GitHub:** https://github.com/phillongworth
- **phillongworth.site:** https://phillongworth.site
- **Bridleway Log:** https://phillongworth.site/bridleway/
- **phillongworth.co.uk:** https://phillongworth.co.uk
- **Cloudflare Dashboard:** https://dash.cloudflare.com

---

## Security Notes

- **SSH:** Key-based authentication only (password disabled)
- **Firewall:** Ports 80/443 closed to the internet; only SSH (22) open
- **Tunnel credentials:** Keep `/etc/cloudflared/*.json` secret
- **Never commit** credentials, `.env` files, or database passwords to git
- **Bridleway Log `.env`:** Contains database credentials — gitignored by default

---

## Quick Start Checklist

When starting a new editing session:

- [ ] Open VS Code
- [ ] Open the project folder (`Ctrl+K Ctrl+O`)
- [ ] Pull latest changes (`git pull`)
- [ ] Make your edits
- [ ] Test locally with Live Server
- [ ] Stage changes (`git add .`)
- [ ] Commit (`git commit -m "description"`)
- [ ] Push (`git push`)
- [ ] Deploy to server (see [Deploying Changes](#deploying-changes))
- [ ] Verify live site (`Ctrl+Shift+R` to hard refresh)
