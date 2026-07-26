# Muddo Agro Chemicals LTD — Official Website (v4 — Spec Theme Rebuild)

Django web application for **Muddo Agro Chemicals LTD (MACL)**, Uganda's MAAIF-registered agrochemical distributor.

This is a full rebuild against `themes.txt`: a real light/dark theme system
(exact hex values from the spec), Inter typeface, light-blue/red/green as the
only accent colors (no orange, no brown, no dark green anywhere), full-bleed
photo heroes on the homepage and every product category page, and every bug
reported in earlier rounds fixed directly in the source rather than left as
a patch to apply.

## Quick Start

```bash
unzip muddo_agro_django.zip && cd muddo_project
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput
python manage.py runserver
```

Open **http://127.0.0.1:8000**

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | muddo@admin2024 |
| Agent | alice / robert / grace / patrick | agent@2024 |

**Change these before going live** — see Admin → Settings.

## ⚠️ If colors still look wrong after deploying

Whitenoise (`CompressedManifestStaticFilesStorage`) fingerprints and caches
static files by content hash. If you deploy new CSS without re-running
`collectstatic`, the browser (and even Whitenoise itself) may keep serving
the old cached file. Always run:

```bash
python manage.py collectstatic --noinput
```

as part of every deploy (the `render.yaml` build command already does this
automatically for Render deploys).

## What this rebuild fixes vs. earlier rounds

- **Theme**: complete rebuild to `themes.txt` — grayscale-free neutral
  surfaces (`#F8FAFC`/`#FFFFFF` light, `#0F172A`/`#1F2937` dark), with
  `#38BDF8` blue, `#EF4444` red, `#4ADE80` green as the *only* accents,
  used at roughly the spec's 70/20/7/3 ratio. Font is Inter throughout.
- **Hero imagery**: homepage and all four product-category pages now use
  full-bleed photographic heroes with a dark scrim + copy on top, matching
  the reference site.
- **"What We Distribute"**: every product is shown (nothing removed),
  each with its real photo on top and its name below, grouped by category.
- **Chat**: fixed the two real bugs — missing CSRF token on send/mark-read
  requests, and mismatched element IDs between `admin/chat.html` and
  `chat.js` that silently kept the chat window from ever opening. Admin's
  `<body>` now also carries `data-user-id`/`data-user-role` so sent vs.
  received bubbles render correctly.
- **Active agents indicator**: live "N agent(s) active now" counter plus
  per-contact online/offline dots, refreshed via `/api/agents/status/`.
- **Delete confirmations**: every destructive action now goes through a
  proper on-brand modal (`confirm-modal.js`) instead of the browser's
  native `confirm()` popup.
- **Store locator map**: real Leaflet + OpenStreetMap map (no API key
  required), pin per outlet, synced with the region filter and search.
- **Split-screen staff login**: left half is an auto-advancing slideshow
  of the four product categories with the logo pinned top-left; right
  half is the sign-in form.
- **Staff Login**: footer-only. Removed from the header/topbar entirely.
- **Admin can edit products**: previously add/delete only; there's now an
  Edit modal pre-filled with the product's current data.
- **Product photos**: every product in `seed_data.py` has its own unique
  image filename slot — no more ten products silently sharing one generic
  placeholder image.

## Still needs real assets from you

- **Product photography**: seed data references `static/images/product_*.jpg`
  filenames that don't all have real files yet — drop in real photos with
  the matching filenames (see `apps/core/management/commands/seed_data.py`)
  and they'll appear automatically, no code changes needed.
- A few of the hero/category images shipped here were drawn from what you
  uploaded (pest photos, sprayer, fertilizer). Swap `static/images/hero_*.jpg`
  for higher-resolution, wider (16:9) shots if you have better source photos.

## Project Structure

```
muddo_project/
├── manage.py
├── requirements.txt / render.yaml / .env.example
├── muddo_project/          ← Django settings/urls/wsgi
├── apps/
│   ├── core/               ← Home, about, contact, search, compare, track
│   ├── products/            ← Catalogue + PDF spec sheets
│   ├── inventory/            ← Stock management
│   ├── agents/               ← Agent accounts, login, presence, PDF reports
│   ├── requests_app/          ← Supply requests
│   ├── messaging/              ← Admin ↔ Agent chat
│   ├── distributors/            ← Store locator + map
│   └── analytics/                ← Admin dashboard, product CRUD incl. edit
├── templates/
├── static/
│   ├── css/  (theme_vars.css is the single source of truth for all color)
│   ├── js/
│   └── images/
└── media/                  ← uploaded product images (auto-created)
```
