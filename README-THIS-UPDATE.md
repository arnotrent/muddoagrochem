# This update — chat fixes, mobile/admin renovation, map locking, new banners

Drop these into your repo at matching paths, then:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Migrations included: `messaging/0002_message_is_broadcast.py`,
`messaging/0003_message_reply_attachment.py`,
`distributors/0002_distributor_country_and_free_region.py`. Nothing
destructive — existing messages and distributors are untouched.

---

## 1. The duplicate-message bug — found and fixed

Real root cause: in `chat.js`, `sendMessage()` rendered your own message
immediately (optimistic UI) but never updated `lastMsgId`. Three seconds
later the poll loop asked the server for "everything after `lastMsgId`" —
which still included the message you'd just sent — so it came back down and
got appended a second time. Fixed by bumping `lastMsgId` right after the
optimistic render.

## 2. Chat now has reply, attachments, and real ticks

- **Reply to a specific message** — hover any bubble, tap the reply icon,
  it quotes that message above your input; send as normal.
- **Attachments** — the paperclip button next to the input lets you attach
  an image or a document (PDF/Word/Excel). Images preview inline in the
  thread; other files show as a downloadable file chip.
- **Read ticks** — sent messages now show a single gray check until read,
  then a blue double-check once the other person has opened the thread.
- **Last seen** — when an agent is offline, admin sees "Last seen HH:MM"
  instead of just "Offline" (using the `last_seen` timestamp you already
  had on the Agent model).

**Important, honest caveat:** this chat is a custom system built into your
own app — it is *not* connected to anyone's real WhatsApp account. There's
no way to show a real WhatsApp "status/story" or a real WhatsApp last-seen,
because this was never wired to WhatsApp's API, only to a `wa.me` deep-link
button elsewhere in the site. What I've built here is a WhatsApp-*style*
experience inside your own admin/agent messaging — reply, attachments,
ticks, presence — using only your own database. A true WhatsApp Business
API integration (and a "Stories"-style ephemeral post feature) is a much
larger, separate project — happy to scope that out with you if it's
something you actually want, but I didn't want to fake it or pretend that's
what this delivers.

**Also flag this now rather than let it surprise you:** file attachments
(and product photos) are saved to local disk (`MEDIA_ROOT`). Render's free
plan has an *ephemeral filesystem* — uploaded files can disappear on the
next deploy/restart unless you add a persistent disk or move media to cloud
storage (e.g. S3 via `django-storages`). This affects product images today,
not just new chat attachments — worth prioritizing before you rely on it.

## 3. Admin panel + Agent Portal on mobile — the actual bug

Neither `admin/base_admin.html` nor `agent/dashboard.html`/`agent/chat.html`
were loading `responsive.css` at all — so none of your mobile rules (hiding
the sidebar, collapsing grids) ever had a chance to run on those pages. This
is exactly why the sidebar stayed "fully outlined" no matter the screen
size. Fixed by linking `responsive.css` on all three.

On top of that:
- Added a hamburger button (`data-sidebar-toggle`, wired in `theme.js`) so
  once the sidebar *does* hide on mobile, there's still a way to open it as
  a slide-over drawer — otherwise you'd lose navigation entirely.
- Added `rgrid-2` / `rgrid-3` / `rgrid-4` / `rgrid-sidebar` utility classes
  and applied them to the two/three/four-column layouts in Dashboard,
  Products, Settings, Agents, Distributors, and the public footer — these
  were all fixed multi-column grids with zero mobile behavior before.
- Chat bubbles, top bar, and input row get extra breathing room under 600px.

This doesn't claim to be a full responsive audit of every page — it fixes
the specific, confirmed breakage (admin/agent panels not loading the
stylesheet at all, plus the footer and several admin forms) rather than
guessing at ones I haven't seen evidence of.

## 4. MACL Admin / Agent banners

Your two uploaded images are now shown as a banner at the top of the Admin
Overview page and the Agent Dashboard (`static/images/banner_admin.png`,
`banner_agent.png`) — they do **not** touch the favicon or the sidebar logo,
which still use your existing `logo_full.png` / `logo_admin.png` exactly as
before.

## 5. Contact & About pages — new banner artwork

Your "Contact Us" and "About Us" graphics now sit at the top of those two
pages (`static/images/hero_contact_banner.png`, `hero_about_banner.png`).
Since these images already carry bold "Contact Us"/"About Us" wordmarks, I
deliberately did *not* stack the old dark-overlay hero text on top of them
(that would've doubled up text and looked cluttered) — instead they render
as a clean full-width banner, with the breadcrumb and intro copy moved into
a normal section immediately below, in your regular text colors. The rest
of both pages (Who We Are, product groups, FAQ) is untouched.

## 6. Distributor map — now locks to the chosen country, then the district

- Selecting a **Country** calls `setMaxBounds()` with that country's
  bounding box, so the admin physically cannot pan or drop a pin outside it
  (previously the box was just decorative — it recentered the view but
  never restricted movement).
- Hitting **"Locate District/City"** tightens the lock further to that
  place's own bounding box (from Nominatim's `boundingbox` response), so
  once you've located "Jinja", you can only place the pin within Jinja —
  not anywhere else in Uganda — until you search a different place or
  change the country.
- A small lock note under the map tells you what it's currently locked to.

## 7. Verifying your 11 already-seeded outlets

I don't have live internet access from this sandbox to call OpenStreetMap's
geocoder directly, so I can't run an automated check on your existing
coordinates from here. I did cross-check all 11 against my own knowledge of
Uganda's geography (town centers for Kampala, Jinja, Mbale, Gulu, Lira,
Mbarara, Masaka, Fort Portal, Iganga, and the Wakiso/Entebbe-road area) —
none of them look like they land in a lake, swamp, or on the wrong side of a
border; they're all within a kilometer or two of their named town centers.

That said, "looks right by eye" isn't the same as verifying it properly.
I've added a management command for that:

```bash
python manage.py verify_distributor_locations
```

Run this **on your deployed server** (e.g. the Render shell), since it
needs outbound internet to reverse-geocode each saved outlet against
OpenStreetMap and print a ✓ / ⚠ / ✗ per outlet — flagging anything that
resolves to the wrong country, doesn't match its assigned district, or
comes back with no address at all (open water). It respects Nominatim's
1-request/second usage limit, so for 11 outlets it takes about 15 seconds.

## Not addressed this round (scoped out on purpose, not forgotten)

- **Avatars / profile photos** for agents — would need a new upload field +
  UI; the model changes needed for it are straightforward but I didn't want
  to half-wire it in the time this round already took.
- **WhatsApp Stories-style "statuses"** — a genuinely separate feature
  (its own model, media expiry, viewer tracking) rather than a tweak to
  existing chat.
- **Real WhatsApp Business API integration** — see the honesty note in
  section 2.

Happy to pick any of these up as their own focused pass.
