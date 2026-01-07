# 🌐 Server Operations Manual: Phil Longworth Digital
**Last Updated:** January 2026  
**Server IP:** `192.168.178.22`  
**User:** `phil`

---

### Repositories
* **Local Path:** `C:\Users\phill\OneDrive\Documents\GitHub\phillongworth-site`
* **Remote Backup:** GitHub (Private Repository)

---

## 🚀 Deployment Workflow
Changes are made locally in VS Code and "pushed" to the live server via a PowerShell script.

## One-Click Deploy
From the VS Code terminal, run:

``
cd C:\Users\phill\OneDrive\Documents\GitHub\phillongworth-site``

``
.\deploy.ps1``

## 💾 Database & Backups
The server is configured to run a daily backup of the web directory and any active databases.

## Manual Backup Command
If you want to create an instant snapshot before making big changes:

``
tar -cvzf ~/backup_$(date +%F).tar.gz /var/www/phillongworth.site/html``


## 🏗 System Architecture
This server uses a **LEMP** stack (Linux, Nginx, MySQL, PHP) running on Ubuntu. It is configured to host multiple domains using Nginx Server Blocks.

### Domains & Directories
| Domain | Path on Server | Nginx Config File |
| :--- | :--- | :--- |
| `phillongworth.site` | `/var/www/phillongworth.site/html` | `/etc/nginx/sites-available/phillongworth.site` |
| `phillongworth.co.uk` | `/var/www/phillongworth.co.uk/html` | `/etc/nginx/sites-available/phillongworth.co.uk` |

### Repositories
* **Local Path:** `C:\Users\phill\OneDrive\Documents\GitHub\phillongworth-site`
* **Remote Backup:** GitHub (Private Repository)

---

## 🚀 Deployment Workflow
Changes are made locally in VS Code and "pushed" to the live server via a PowerShell script.

### One-Click Deploy
From the VS Code terminal, run:
powershell
``.\deploy.ps1``


**What this script does:**

1. Syncs local files to `/var/www/phillongworth.site/html` via `scp`.
2. Sets folder ownership to `www-data` (Nginx user).
3. Reloads the Nginx service to apply changes.

---

## 🔒 Security & Access

* **Authentication:** SSH Keys Only (Password login is **DISABLED**).
* **Authorized Devices:** 1. Lenovo Laptop
2. Main Windows Desktop
* **SSH Alias:** Configured in `~/.ssh/config` as `myserver`.

### Connection Command

```powershell
ssh myserver
```

---

## 🛠 Troubleshooting Advice

### "Permission Denied (publickey)"

* **Cause:** Your current device's SSH key isn't in the server's "Authorized" list.
* **Fix:** Copy your `id_ed25519.pub` and paste it into `/home/phil/.ssh/authorized_keys` on the server using an already-authorized device.

### "Nginx Test Failed" (Site Down)

If you make manual changes to Nginx and the site breaks, run:

```bash
sudo nginx -t
```

This will tell you the exact line number where the typo is located.

### "Certificate Expired" (HTTPS Error)

Certbot handles this automatically, but you can force a check with:

```bash
sudo certbot renew --dry-run
```

###  How to Restore (The "Fire Drill")
If you ever accidentally delete your site, you just "unzip" your latest backup. You would run:

Example: Extracting the backup from Jan 6th back to your site folder

```bash 
sudo tar -xzf /home/phil/backups/site_backup_2026-01-06.tar.gz -C /
```

---

## ❓ FAQ

**Q: How do I add a third domain?**

1. Create a new folder: `/var/www/newdomain.com/html`.
2. Create a new Nginx config in `sites-available`.
3. Link it: `sudo ln -s /etc/nginx/sites-available/newdomain.com /etc/nginx/sites-enabled/`.
4. Run Certbot for the new domain.

**Q: Where can I see who is visiting my site?**
Check the live Nginx access logs:

```bash
tail -f /var/log/nginx/access.log
```

**Q: How do I restart the server if it's sluggish?**

```bash
sudo reboot
```

*Note: All services (Nginx, Certbot) are set to start automatically on boot.*

---
## Guide to Markdown basic syntax
https://www.markdownguide.org/basic-syntax/
