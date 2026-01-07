# 🌐 Server Operations Manual: Phil Longworth Digital
**Last Updated:** January 2026  
**Server IP:** `192.168.178.22`  
**User:** `phil`

---

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
```powershell
.\deploy.ps1
