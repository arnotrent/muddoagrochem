# This update — new photos, a real chat attachment system, product reviews, and company leadership

Drop into your repo at matching paths (this zip is a **complete, deployable copy of the whole
project** — every file is here, not just a diff), then:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

No existing images were replaced or removed. M-D AMETRYN was left exactly as you shipped it (no
edits, no new photos on that product). Everything below is additive.

---

## 1. New product photography — added, nothing replaced

Five new images from your latest upload are now on the site, placed where they're relevant:

| File | Used on |
|---|---|
| `static/images/gallery_mdfos_pests.jpg` | Pesticides page gallery strip + M-D FOS product gallery |
| `static/images/gallery_pesticide_range.jpg` | Pesticides & Fungicides gallery strip + M-D THION / TOP-LAXLY M / M-D ACELEMECTIN galleries |
| `static/images/gallery_herbicide_shelf.jpg` | Herbicides page gallery strip + M-D AMETRYN / MAX 2,4-D galleries |
| `static/images/gallery_crops_collage.jpg` | Herbicides page gallery strip |
| `static/images/gallery_range_lineup.jpg` | Fertilizers & Equipment gallery strip + MUDDOSATE gallery |
| `static/images/product_ametryn.jpg`, `product_ametryn_original.jpg` | M-D AMETRYN's own product page (main + gallery) |

These render as a photo strip near the top of each category page (`templates/products/_product_list.html`)
and as an extra thumbnail row on the affected products' detail pages — your existing hero images,
product photos and everything else are untouched.

## 2. M-D AMETRYN — added as a genuine product (was missing from the catalogue)

Added to `apps/products/catalog_additions.py` (used by both a data migration for existing databases
and by `seed_data.py` for fresh ones), so it appears automatically either way:

- **M-D AMETRYN 500 g/L SC** — selective triazine (Group 5) herbicide for annual broadleaved weeds
  and annual grasses in **sugarcane, pineapple, cassava and tomatoes**. 1-litre packs.
- Every fact came straight off the label in your bottle photo. The label's dosage table wasn't
  legible in the photo, so the dosage field says "follow the rate and timing on the label" rather
  than inventing a number.
- On an **existing** database, run `python manage.py migrate` and it's added once, automatically
  (migration `products.0003_add_md_ametryn_and_galleries`, safe to run twice).

## 3. Chat attachments — rebuilt as a real system, not a patch

This was the biggest piece. Previously chat took **one file per message** (`Message.attachment`),
stored under public `/media/`, with no preview beyond "is it an image". It's now:

**Backend (`apps/messaging/`)**
- `models.py` — new `Attachment` model: one row per file, `message` nullable until the message is
  actually sent (so upload can start before you hit send). Old `Message.attachment` rows still work
  and still render — nothing breaks for messages sent before this update.
- `uploads.py` — validation: extension **and** file-header ("magic bytes") must agree, blocks
  executables/scripts/active-web-content outright, enforces size and per-message file-count limits,
  and has an optional ClamAV hook (`CHAT_CLAMAV_ENABLED=True`, needs `pip install pyclamd` and a
  running `clamd`) — off by default, fails open if the scanner isn't reachable so it never blocks
  uploads by accident.
- `storage.py` — attachments are stored **outside** `MEDIA_ROOT` (`PRIVATE_MEDIA_ROOT`, or a private
  S3 prefix when `USE_S3_MEDIA` is on) and are **never** mounted under `/media/`. The only way to
  reach one is `apps/messaging/views.py:api_attachment_file`, which re-checks that the requester is
  actually a party to that conversation (or staff) before streaming a byte — 404, not 403, if not,
  so the file's existence isn't revealed either.
- `views.py` — new endpoints: `upload`, `upload/<id>/delete`, `attachments/<id>/file` (streams with
  HTTP Range support, so video seeking works, and the **original filename** in the download), plus
  `typing`, `search`, `info`, `files` (Shared Files), `report`. `send` now takes `attachment_ids`,
  is idempotent via a client-generated `client_id` (a retried request never double-sends), and
  delivery/read ticks are tracked per-message (`delivered`, `delivered_at`, `read_at`).
- Original files are **never converted** — stored under a random name on disk, original filename +
  MIME + extension kept as metadata, served back with the original name via `Content-Disposition`.

**Frontend**
- `static/js/chat.js` — full rewrite: multi-file picker + drag-and-drop, per-file upload progress
  bar with retry-on-failure, a unified attachment viewer (image lightbox with next/prev, embedded
  PDF viewer, video/audio players, plain-text preview, a download card for everything else),
  in-conversation search, a conversation-info side panel with Shared Files (filterable, searchable),
  a typing indicator, and real delivery/read ticks (⏱ sending → ✓ delivered → ✓✓ blue read).
- `static/css/chat.css` — all the new UI's styling, loaded after `admin.css` on both
  `templates/admin/chat.html` and `templates/agent/chat.html`, which both got the new toolbar
  (search + info buttons), drop-zone overlay, and info-panel markup.

**Security specifics** (per your spec's "Security" section):
- Authenticated + authorized on every access; agents only see conversations they're a party to,
  admins see everything, exactly as before.
- Never trusts the extension alone — validates the file's actual header bytes against it.
- Storage identifiers are random UUIDs; storage paths are never exposed to the client.
- Executable/script/active-content extensions are blocked outright (`.exe .msi .bat .sh .js .html
  .php` etc. — see `BLOCKED_EXTENSIONS` in `uploads.py`); everything else (docs, images, spreadsheets,
  video, audio, archives) is accepted per the spec's "any format" requirement.
- Per-user rate limiting on send/upload/report endpoints (in-process cache-based; fine for a single
  Gunicorn box, swap `CACHES` in `settings.py` for Redis if you scale to multiple workers).

## 4. Product reviews — public submission + admin moderation

- `apps/products/models.py` — `ProductReview` (rating 1–5, name, optional location/email, title,
  comment, `status`: pending/approved/rejected). **Nothing shows on the site until an admin
  approves it.**
- Public form on every product page (`templates/products/product_detail.html`, `#write-review`):
  honeypot field + a timed form-token (rejects submissions faster than 3 seconds) + per-visitor rate
  limiting (hashed IP, not stored raw) — all server-side in `apps/products/views.py:submit_review`,
  no JS dependency for the actual validation.
- Star average + rating breakdown + review list on the product page; a small ★ rating badge on
  category-page product cards once a product has approved reviews.
- Admin: **Reviews** in the sidebar → pending/approved/rejected tabs, approve/reject/delete, and a
  "Pending Reviews" KPI card + list on the dashboard.

## 5. Company Leadership section

- `apps/core/models.py` — `LeadershipMember` (name, title, bio, photo, order, active). Seeded with
  three "Name to be announced" placeholders by migration `core.0005_leadershipmember` — replace
  these from Admin → Leadership whenever you have the real names/photos/bios.
- Renders on the About page between "Who We Are" and "What We Distribute" — only when at least one
  member is marked active, so it disappears cleanly if you ever delete them all.
- Admin: **Leadership** in the sidebar → add/edit/delete, with a photo upload.

## 6. Smaller things bundled in

- `settings.py`: session/CSRF cookies hardened (`HttpOnly`, `SameSite=Lax`, `Secure` when
  `DEBUG=False`), a proper cache backend added (file-based; needed for chat rate-limiting and typing
  indicators), upload size limits wired to Django's own `DATA_UPLOAD_MAX_MEMORY_SIZE`.
- `apps/core/urls.py` / `views.py`: restored the `/health/` and `/api/v1/health/` endpoints your
  earlier round added (documented in your project notes as fixing a false "service is down" signal).
- Admin sidebar: added **Reviews** and **Leadership**, both with the same active-state highlighting
  as the rest of the nav.

## 7. What was deliberately left alone

- **M-D AMETRYN's own product images** — none added, exactly as asked.
- Every existing image, product, and page not mentioned above.
- WebSockets — chat still polls, per your standing preference.
- Admin-editable FAQs stayed admin-editable (unchanged); nothing about that was touched.

## Migration order for an existing database

```bash
python manage.py migrate
```

New migrations, in dependency order: `products.0002_productimage_productreview` →
`products.0003_add_md_ametryn_and_galleries` (adds M-D AMETRYN + galleries), `messaging.0004_attachment_system`,
`core.0005_leadershipmember`. All are additive — nothing is dropped or altered destructively.

## New environment variables (all optional, all have safe defaults)

| Variable | Default | Purpose |
|---|---|---|
| `CHAT_MAX_UPLOAD_MB` | `25` | Max size per chat attachment |
| `CHAT_CLAMAV_ENABLED` | `False` | Turn on the optional ClamAV malware scan for uploads |

`PRIVATE_MEDIA_ROOT` (chat attachment storage) defaults to `<project>/private_media/` on local disk,
or automatically moves to a private S3 prefix when your existing `AWS_*` variables are set.
