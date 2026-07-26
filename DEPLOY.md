# Muddo Agro Chemicals LTD — Deployment Guide

## 🚀 Quick Start (Development)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit DJANGO_SECRET_KEY at minimum
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Open **http://127.0.0.1:8000**

## 🔑 Default Credentials

| Role | URL | Username | Password |
|------|-----|----------|----------|
| Administrator | /login/ → Administrator | admin | muddo@admin2024 |
| Field Agent | /login/ → Field Agent | alice / robert / grace / patrick | agent@2024 |

> ⚠️ Change all passwords immediately via Admin → Settings before going live.

## ☁️ Deploy on Render.com

`render.yaml` is already configured — connect the repo and Render will run:
```
pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput && python manage.py seed_data
```
and start with:
```
gunicorn muddo_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## 🖥️ Production Setup (Ubuntu + Nginx + Gunicorn)

```bash
sudo apt update && sudo apt install python3-pip python3-venv nginx certbot python3-certbot-nginx -y
sudo mkdir -p /var/www/muddo_agro && cd /var/www/muddo_agro
# upload code here
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput

sudo cp muddo_agro.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now muddo_agro

sudo cp muddo_agro.nginx /etc/nginx/sites-available/muddo_agro
sudo ln -s /etc/nginx/sites-available/muddo_agro /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## ⚠️ Every deploy, always re-run collectstatic

```bash
python manage.py collectstatic --noinput
```

`STATICFILES_STORAGE` is Whitenoise's `CompressedManifestStaticFilesStorage`,
which fingerprints files by content hash. If you skip this step after
changing any CSS/JS/template, the live site will keep serving the old
cached version even though your source files are correct — this was the
root cause of earlier color-theme fixes not showing up.

## ✅ Production Checklist

- [ ] Change admin password and all agent passwords (Admin → Settings)
- [ ] Set `DEBUG=False` in `.env`
- [ ] Set a strong `DJANGO_SECRET_KEY`
- [ ] Configure Gmail App Password for email notifications
- [ ] Run `python manage.py collectstatic` on every deploy
- [ ] Replace placeholder product photos in `static/images/` with real ones
      matching the filenames in `apps/core/management/commands/seed_data.py`
- [ ] Test contact form email delivery
- [ ] Test PDF spec sheet download
- [ ] Verify the store locator map loads (needs outbound access to
      `unpkg.com` and `tile.openstreetmap.org`)
