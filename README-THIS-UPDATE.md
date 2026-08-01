# This update — attachments, group chat, profiles, dashboard charts, About redesign

Drop these into your repo at matching paths, then:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

New migrations this round: `agents/0002_agent_display_avatar.py`,
`core/0002_staffprofile.py`. (Everything from earlier rounds — messaging,
distributors — is also included in this same folder tree.)

---

## 1. Attachments not opening — the real bug

Your `urls.py` only served `/media/` when `DEBUG=True`:
```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
On Render, `DEBUG=False`, so **every** uploaded file — chat attachments and
product photos alike — 404'd. Nothing was wrong with the files themselves
or their format; they were just never being served. Fixed by serving media
regardless of `DEBUG`.

**Still worth knowing:** Render's free tier has an ephemeral filesystem, so
uploaded files can vanish on the next deploy/restart even with this fix.
That's a separate, bigger problem (needs a persistent disk or S3 via
`django-storages`) — this fix makes attachments work *right now*, not
necessarily forever.

## 2. Chat is now a real group — "Team" channel

Renamed "All Agents" → **"Team (Everyone)"**, and it's no longer admin-only:
any agent can post there too, and it's visible to admin + every agent.
Received messages in Team show who sent them (name + their photo, like a
WhatsApp group) since more than one person posts there now.

**Agents now have a full contact list**, not just a single admin thread:
Team (pinned), Admin, and every other active agent — so agents can message
each other directly, not only through admin.

## 3. Chat on mobile — proper master/detail navigation

Previously both the contact list and the open conversation were squeezed
into one column at once. Now on narrow screens you see the contact list
full-width; tapping a contact slides the conversation over it full-width,
with a back arrow to return — the same pattern WhatsApp/Messenger use, and
it applies to both the admin and agent chat pages since they now share the
same layout.

## 4. Self-service profiles — no admin approval needed

New "My Profile" page for both admin and agents (linked in both sidebars):
- Change your **display name** any time — saves immediately, no approval
  step.
- Upload a **profile photo** — shows up as your avatar everywhere in chat
  (contact list, message bubbles, topbar).
- Your **original account name stays on file** and is shown as a quiet
  "originally X" line under your chosen display name — both on your own
  profile page and in Admin → Field Agents, so admin always has the
  original reference even after someone changes their public name.

## 5. Sidebar logo — fixed to your real MACL logo

The admin sidebar was using a separate small `logo_admin.png` (which is
what showed blurry/broken in your screenshot) instead of your actual site
logo. Both admin and agent sidebars now use `logo_full.png` — your one real
logo — consistently. The two "MACL Admin"/"MACL Agent" wall-plaque graphics
you sent stay exactly where they were: banners at the top of the two
dashboards, nowhere near the sidebar or the browser tab icon.

## 6. Banners now fill their container

Previous banners used `object-fit:contain`, which is exactly what caused
those dark letterbox bars on either side. Switched to `object-fit:cover` so
the image fills the full width with no gaps (small crop on the edges is the
trade-off, but no more bars).

## 7. Admin Dashboard — animated + interactive charts

- KPI numbers now count up from 0 on page load.
- Three real charts, built from your existing `/api/analytics/` endpoint
  (it existed already, just wasn't rendered anywhere): a 14-day enquiries
  trend line, a supply-requests-by-status doughnut, and a
  products-by-category doughnut. Colors are pulled live from your theme
  tokens, so they follow light/dark mode automatically. Uses Chart.js via
  CDN (same pattern as Leaflet — no new backend dependency).

## 8. About Us — redesigned product showcase + new photo

The old "What We Distribute" section repeated the category icon twice (an
icon badge *and* a separate thumbnail image side by side) and used plain
1:1 square photo tiles with no real card styling — that's the "unprofessional"
look. Replaced with: one clean category header (icon + title + blurb, no
duplicate), and a proper 4:3 card grid matching the visual language used
elsewhere on the site (hover lift, consistent border/radius, category
label). Also swapped the old tomato-crop photo in "Who We Are" for your new
trust/handshake image, since "Trust, Respect, Integrity, Honesty" fits that
section's message better than a crop photo that already appears on the
homepage.

## Still not addressed (flagging honestly, not quietly dropped)

- **Real WhatsApp Business API / Stories** — as noted last round, this chat
  is a custom system, not connected to anyone's actual WhatsApp account.
  Group chat, reply, attachments, and read ticks are now genuinely
  WhatsApp-*like*, built entirely on your own data — a real WhatsApp
  integration is a separate, much larger project.
- **Persistent file storage** — see the caveat in section 1. Worth doing
  before you rely heavily on uploads (product photos or chat attachments).
- A full visual QA pass on every single admin sub-page's chart/animation
  potential (only the main Dashboard got charts this round, since that's
  what was asked for) — happy to extend the same treatment (e.g. an
  Inventory trend chart, an Enquiries-by-subject breakdown) if useful.
