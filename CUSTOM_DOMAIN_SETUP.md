# Custom Domain Connection & Production Deployment Guide
## LegalMetriX Packaged Commodity Compliance & Verification System

This document outlines the step-by-step procedure for deploying LegalMetriX under a custom production domain (e.g., `inspect.legalmetrix.org`, `compliance.yourdomain.com`, or official department subdomains).

---

### 1. Architectural Overview

LegalMetriX uses a high-performance, container-ready architecture:
- **Application Server**: WSGI (Gunicorn / Waitress / Flask) with `werkzeug.middleware.proxy_fix.ProxyFix` pre-configured to respect reverse-proxy host headers (`X-Forwarded-Host`, `X-Forwarded-Proto`, `X-Forwarded-For`).
- **Reverse Proxy**: Nginx or Caddy terminating TLS 1.3 encryption.
- **SSL Certificate**: Let's Encrypt (Certbot) with automated renewal.

---

### 2. Step 1: DNS Record Configuration

Configure your domain DNS registrar (Cloudflare, AWS Route 53, GoDaddy, Namecheap, etc.) with the following records pointing to your production server's public IP address:

| Type | Host / Name | Value / Target | TTL | Description |
| :--- | :--- | :--- | :--- | :--- |
| **A** | `inspect` (or `@` for root) | `YOUR_SERVER_PUBLIC_IP` | Auto / 300s | Points custom domain to server IP |
| **CNAME** | `www.inspect` | `inspect.yourdomain.com` | Auto / 300s | Canonical alias (if using www) |
| **CAA** | `@` | `0 issue "letsencrypt.org"` | Auto | Restricts SSL authority to Let's Encrypt |

> **Note for Cloudflare users**: Initially set the SSL/TLS mode to **Full (Strict)** and verify that the A record is resolving before running Certbot.

---

### 3. Step 2: Production WSGI Service (Systemd)

Create a systemd service file at `/etc/systemd/system/legalmetrix.service`:

```ini
[Unit]
Description=LegalMetriX Compliance Application Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/legalMatrix
Environment="PATH=/var/www/legalMatrix/venv/bin"
Environment="GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE"
Environment="FLASK_ENV=production"
ExecStart=/var/www/legalMatrix/venv/bin/gunicorn \
    --workers 4 \
    --threads 2 \
    --bind 127.0.0.1:5000 \
    --access-logfile /var/log/legalmetrix/access.log \
    --error-logfile /var/log/legalmetrix/error.log \
    app:app

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo mkdir -p /var/log/legalmetrix
sudo chown -R www-data:www-data /var/log/legalmetrix
sudo systemctl daemon-reload
sudo systemctl enable legalmetrix
sudo systemctl start legalmetrix
sudo systemctl status legalmetrix
```

---

### 4. Step 3: Nginx Reverse Proxy Configuration

Create `/etc/nginx/sites-available/legalmetrix.conf`:

```nginx
# HTTP - Redirect all traffic to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name inspect.yourdomain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS - Secure Production Endpoint
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name inspect.yourdomain.com;

    # SSL Certificate Paths (Managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/inspect.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/inspect.yourdomain.com/privkey.pem;

    # Modern TLS Security Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Max upload size (Set to 25M for high-resolution packaging label photos)
    client_max_body_size 25M;

    # Static Assets Cache
    location /static/ {
        alias /var/www/legalMatrix/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Favicon Direct Serving
    location = /favicon.ico {
        alias /var/www/legalMatrix/static/favicon.svg;
        default_type image/svg+xml;
    }

    # ProxyPass to Local Flask/Gunicorn Application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        
        # Forward custom domain and client headers to Flask ProxyFix
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;

        # Timeouts for Gemini Multimodal & OCR Pipelines
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

Enable the Nginx site configuration:
```bash
sudo ln -s /etc/nginx/sites-available/legalmetrix.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### 5. Step 4: Issue Free SSL Certificate via Let's Encrypt

Run Certbot to obtain and automatically install the SSL certificate:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d inspect.yourdomain.com --agree-tos -m admin@yourdomain.com
```

Test automatic renewal:
```bash
sudo certbot renew --dry-run
```

---

### 6. Verification Checklist

Once completed, verify the following live health checks:
1. **Domain Resolution**: `curl -I https://inspect.yourdomain.com` returns `HTTP/2 200`.
2. **Favicon**: `https://inspect.yourdomain.com/favicon.ico` displays the official SVG balance scale icon.
3. **Statutory Pages**:
   - `https://inspect.yourdomain.com/privacy` loads the Privacy Policy without errors.
   - `https://inspect.yourdomain.com/terms` loads the Terms & Conditions without errors.
4. **Header Integrity**: Reverse proxy headers preserve `https` and client IP without SSL mixed-content warnings.
