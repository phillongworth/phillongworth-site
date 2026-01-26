# Server Operations Manual: Phil Longworth Digital

**Last Updated:** January 2026
**Server:** `optiplex7040-server`
**User:** `phil`

---

## Architecture Overview

All sites are served through a **Cloudflare Tunnel** - no ports are open to the internet. Traffic flows:

```
Internet → Cloudflare Edge → Tunnel → Local Nginx/Apps
```

### Benefits
- No open ports (80/443 closed)
- Cloudflare handles SSL certificates automatically
- DDoS protection included
- No need for Let's Encrypt/Certbot

---

## Domains & Configuration

| Domain | Content | Served By |
|--------|---------|-----------|
| `phillongworth.co.uk` | Static site | Nginx → `/var/www/phillongworth-co-uk/html` |
| `phillongworth.site` | Static site | Nginx → `/var/www/phillongworth-site/html` |
| `www.phillongworth.site` | Static site | Nginx → `/var/www/phillongworth-site/html` |
| `map.phillongworth.site/bridleway/` | Bridleway Log app | Docker → `localhost:6080` |

---

## Key Files & Locations

### Cloudflare Tunnel
| File | Purpose |
|------|---------|
| `/etc/cloudflared/config.yml` | Tunnel routing configuration |
| `/etc/cloudflared/*.json` | Tunnel credentials (keep secret) |
| `/etc/systemd/system/cloudflared.service` | Systemd service file |

### Nginx
| File | Purpose |
|------|---------|
| `/etc/nginx/sites-available/phillongworth.co.uk` | phillongworth.co.uk config |
| `/etc/nginx/sites-available/phillongworth.site` | phillongworth.site config |
| `/etc/nginx/sites-available/map.phillongworth.site` | map subdomain config |
| `/etc/nginx/sites-enabled/` | Symlinks to enabled sites |

### Web Content
| Path | Content |
|------|---------|
| `/var/www/phillongworth-co-uk/html` | phillongworth.co.uk files |
| `/var/www/phillongworth-site/html` | phillongworth.site files |
| `/var/www/bridleway-log/` | Bridleway Log application |

---

## Current Tunnel Configuration

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

## Common Tasks

### Check Service Status
```bash
# Cloudflare Tunnel
sudo systemctl status cloudflared

# Nginx
sudo systemctl status nginx

# Bridleway Log (Docker)
docker ps
```

### Restart Services
```bash
# After changing tunnel config
sudo systemctl restart cloudflared

# After changing nginx config
sudo nginx -t && sudo systemctl reload nginx

# Restart Bridleway Log
cd /var/www/bridleway-log && docker compose restart
```

### View Logs
```bash
# Tunnel logs
journalctl -u cloudflared -f

# Nginx access logs
tail -f /var/log/nginx/access.log

# Nginx error logs
tail -f /var/log/nginx/error.log

# Bridleway Log
docker compose -f /var/www/bridleway-log/docker-compose.yml logs -f web
```

### List Active Tunnels
```bash
cloudflared tunnel list
cloudflared tunnel info phillongworth-co-uk
```

---

## How to Add a New Map to map.phillongworth.site

1. **Deploy your app** (e.g., on port 6090)

2. **Update nginx config:**
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

3. **Reload nginx:**
   ```bash
   sudo nginx -t && sudo systemctl reload nginx
   ```

4. **Access at:** `https://map.phillongworth.site/newmap/`

---

## How to Add a New Domain

1. **Add domain to Cloudflare** (if not already there)

2. **Add CNAME record in Cloudflare DNS:**
   - Type: `CNAME`
   - Name: `@` (or subdomain)
   - Target: `12a6f249-55ad-4062-857f-6cbbce47f429.cfargotunnel.com`
   - Proxy: Enabled (orange cloud)

3. **Update tunnel config:**
   ```bash
   sudo nano /etc/cloudflared/config.yml
   ```

   Add before the catch-all:
   ```yaml
     - hostname: newdomain.com
       service: http://localhost:80
   ```

4. **Create nginx config:**
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

5. **Enable site and restart:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/newdomain.com /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   sudo systemctl restart cloudflared
   ```

---

## Troubleshooting

### Site Not Loading

1. **Check tunnel status:**
   ```bash
   sudo systemctl status cloudflared
   ```

2. **Check tunnel connections:**
   ```bash
   cloudflared tunnel info phillongworth-co-uk
   ```
   Should show 4 connections to Cloudflare edge.

3. **Test locally:**
   ```bash
   curl -I http://localhost -H "Host: phillongworth.site"
   ```

### 502 Bad Gateway

The backend service isn't responding.

```bash
# Check if nginx is running
sudo systemctl status nginx

# Check if Docker app is running (for map.phillongworth.site)
docker ps
```

### Tunnel Won't Start

1. **Check config syntax:**
   ```bash
   cat /etc/cloudflared/config.yml
   ```
   - Ensure no extra indentation on top-level keys
   - YAML is space-sensitive

2. **Check logs:**
   ```bash
   journalctl -u cloudflared -n 50
   ```

3. **Common errors:**
   - `yaml: line X: mapping values are not allowed` = indentation problem
   - `no such file or directory` = credentials file missing

### DNS Not Resolving

1. **Check Cloudflare DNS panel** - ensure CNAME records exist and are proxied

2. **Test DNS resolution:**
   ```bash
   dig yourdomain.com @1.1.1.1 +short
   ```
   Should return Cloudflare IPs (104.x.x.x or 172.x.x.x)

3. **DNS propagation** - may take a few minutes after adding records

### Nginx Config Errors

```bash
# Test configuration
sudo nginx -t

# View specific error
sudo nginx -t 2>&1
```

Common fixes:
- Missing semicolon at end of line
- Broken symlink in sites-enabled
- Duplicate server_name across configs

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

### Restore from Backup
```bash
sudo tar -xzf ~/backup_2026-01-25.tar.gz -C /
```

---

## Deployment Workflow

Changes are made locally and pushed via PowerShell script or git.

### From Windows (VS Code)
```powershell
.\deploy.ps1
```

### From Server (Git Pull)
```bash
cd /var/www/phillongworth-site
git pull
```

---

## Security Notes

- **SSH:** Key-based authentication only (password disabled)
- **Firewall:** Ports 80/443 are closed; only SSH (22) is open
- **Tunnel credentials:** Keep `/etc/cloudflared/*.json` secret
- **Never commit** credentials or `.env` files to git

---

## Quick Reference

| Task | Command |
|------|---------|
| Check tunnel | `sudo systemctl status cloudflared` |
| Restart tunnel | `sudo systemctl restart cloudflared` |
| Reload nginx | `sudo nginx -t && sudo systemctl reload nginx` |
| View tunnel logs | `journalctl -u cloudflared -f` |
| List tunnels | `cloudflared tunnel list` |
| Test site locally | `curl -I http://localhost -H "Host: domain.com"` |
