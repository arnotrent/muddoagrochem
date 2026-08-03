# This update — copyright/nav fixes, editable site content, real duplicate-message fix, storage reliability, product photo display

Drop into your repo at matching paths, then:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

New migrations: `core/0003_sitesettings_faq.py` (schema) and
`core/0004_seed_site_content.py` (data — copies your current FAQs and
company details into the new editable tables, so nothing changes visually
until you edit them in Admin → Site Content).

---

## 1. Copyright + mobile nav

- Footer now reads "© {year} Muddo Agro Chemicals LTD. **All Rights
  Reserved.** MAAIF-Registered Distributor."
- **Staff Login removed from the mobile hamburger menu.** It's footer-only
  now on every screen size — the mobile drawer only shows it if you're
  *already* logged in (as your Admin Panel/Agent Portal + Logout links),
  never as a login prompt for visitors.

## 2. Site content is now admin-editable

New **Admin → Site Content** page. Two things you can change without
touching code:
- **Company info**: year founded, phone (+ optional second number), email,
  address, business hours, WhatsApp number, Facebook URL. These feed the
  About page, Contact page, and the site footer directly.
- **FAQs**: add, edit, hide, or delete — shown on the About page in the
  order you set.

Your current hardcoded content was copied into the database automatically
by the migration, so the site looks identical until you actually change
something.

## 3. The office-room banner photos

Swapped `banner_admin.png` / `banner_agent.png` for the two photos you
specified — the rooms with the "MACL ADMIN"/"MACL AGENT" signage on the
wall — replacing the flatter logo-plaque renders from last round.

## 4. Chat — the real duplicate-message cause, found

Every previous "duplicate message" symptom you've shown had one thing in
common: an attachment, which takes longer to upload than plain text — and
the Send button had no "busy" state. A second click (or a second Enter,
easy to do when the UI looks unresponsive during upload) fired a second,
genuinely separate POST to the server. That's not a rendering bug, it's
really two messages. Fixed by disabling Send (and ignoring Enter) the
moment a send starts, until it finishes.

## 5. Chat — messages hidden below the visible area

Real cause: a classic flexbox gotcha. `.chat-msgs-wrap` had `flex:1;
overflow-y:auto`, but its parent containers didn't have `min-height:0` —
so instead of the message list scrolling *inside* a fixed-height box, the
whole box grew to fit its content, pushing the newest messages below the
viewport with nothing to scroll. Added `min-height:0` through the whole
chain, and fixed the mobile chat layout specifically: it was using
`height:auto` on small screens, which is the same problem in a more
literal way. Now it uses a definite `calc(100vh - …)` height on mobile too.

## 6. Emoji picker

A 🙂 button next to the attachment button opens a small emoji grid;
picking one inserts it at the cursor position in the message box. Works
for admin, agents, and the Team channel alike.

## 7. Attachments/avatars — why they weren't really working, and what's fixed vs. what needs your input

Two separate problems were stacked on top of each other:

- **Django wasn't serving `/media/` at all in production** — this was
  fixed two rounds ago (`urls.py` no longer gates media serving behind
  `DEBUG`). If you hadn't redeployed that fix yet, this alone explains
  broken images/avatars.
- **Render's free-tier disk is ephemeral** — even with media serving
  fixed, uploaded files disappear the next time the service restarts or
  redeploys (Render's own documented behavior, not something code alone
  can fix). This is very likely why you're still seeing broken images
  even after redeploying — the file was there right after upload, then
  gone after the service spun down or redeployed.

This round adds **optional S3-backed storage** (`django-storages` +
`boto3`, already in `requirements.txt`). Set these three environment
variables on Render (`render.yaml` now lists them, `sync: false` so you
fill them in from the dashboard) and uploads switch automatically to S3,
surviving restarts:
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME
```
Leave them unset and everything behaves exactly as before — nothing
breaks, but uploads will keep disappearing on restart until you add an S3
bucket (or a Render persistent disk, the paid alternative). I can't create
the actual S3 bucket for you from here — that's an AWS account/console
step — but the code is ready the moment you do.

## 8. Product photos — now actually visible

Root cause: `.product-card-img` used `object-fit:cover` in a 210px box —
which crops tall, narrow bottle/sachet photos — plus a dark gradient sat
across the bottom of every image, washing it out further. Product photos
now use `object-fit:contain` against a neutral background with padding, so
the whole pack shot is visible with nothing cropped or darkened; the image
area is also taller (240px) for legibility. Same fix applied to the
product detail page's hero image and the quick-view modal. Admin's product
table thumbnails are now click-to-view-full-size and no longer crop either.

## Still outstanding, flagged honestly

- The S3 bucket itself needs to be created and its credentials added by
  you (or by me in a future session if you'd like guided help) — I can't
  provision AWS resources from this sandbox.
- A few remaining hardcoded phone/email mentions elsewhere in the site
  (e.g. the homepage's "Not Sure Which Product" CTA) weren't switched to
  the new editable fields this round — only About, Contact, and the
  footer were in scope for this pass. Happy to sweep the rest next time.
