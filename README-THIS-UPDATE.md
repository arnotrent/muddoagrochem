# This update — two feature sets

Drop these files into your existing repo at the same paths (they replace the
files of the same name), then run:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Two new migrations are included — one for the messaging app (chat), one for
distributors (country field). Nothing else needs to change; existing data
(all your current outlets) is automatically tagged `country="Uganda"`.

---

## 1. Chat system — real fix + broadcast

**Root cause of "chat doesn't work / no recent chats":** `chat.js` was
calling endpoints like `/api/chat/send` and `/api/chat/mark-read` — missing
the trailing slash your `urls.py` requires. In production (`DEBUG=False`),
Django's `APPEND_SLASH` redirects those POSTs, and browsers convert POST→GET
on that redirect, silently dropping the message body and CSRF token. That's
the actual bug — fixed by pointing every fetch at the exact URLs.

On top of the fix:
- **Recent chats list** — admin's sidebar now sorts agents by unread-first,
  then most recent activity, and shows a WhatsApp-style last-message preview
  + timestamp under each name.
- **Broadcast** — a pinned "📢 All Agents" thread at the top of the admin
  chat lets you message every active agent at once. Agents see broadcast
  messages appear automatically in their own admin thread, tagged
  "Broadcast" so it's clear it wasn't a 1:1 message. One-on-one chat still
  works exactly as before.
- Polished the chat CSS (search box, contact previews, badges) — all still
  built from your existing `theme_vars.css` tokens, no new colors introduced.

Files: `apps/messaging/models.py`, `apps/messaging/migrations/0002_message_is_broadcast.py`,
`apps/messaging/views.py`, `templates/admin/chat.html`, `static/js/chat.js`,
`static/css/admin.css` (chat section only — rest of the file unchanged).

**Known simplification:** broadcast messages are one shared row (not one
per agent), so "read" status on a broadcast is shared across all agents
rather than tracked per-agent. Good enough for a notify-everyone feature;
flag it if you later want per-agent read receipts on broadcasts.

## 2. Distributor locations — country-first, validated

New flow in Admin → Distributors:
1. Pick **Country** first (Uganda, Kenya, Tanzania, Rwanda, Burundi, South
   Sudan, DR Congo, Other) — the map recentres to that country.
2. Enter **Region/State** and **District/City** (Uganda gets autosuggest for
   its four regions).
3. Hit **"Locate District/City"** — it geocodes what you typed (via free
   OpenStreetMap Nominatim, no API key) and flies the map there.
4. **Click the map** (or drag the pin) to set the *exact* spot. As you do,
   it reverse-geocodes the point and shows a live check: a green "✓ inside
   &lt;country&gt;, near &lt;place&gt;" or an amber warning like "this looks
   like open water" or "this looks like it's in Kenya, not Uganda."
5. The form won't submit until a pin is placed, **and** the server
   double-checks the coordinates fall inside a rough bounding box for the
   selected country before saving — so a stray pin in the ocean or on the
   wrong continent gets rejected server-side even if someone bypasses the
   browser check.

Editing an existing outlet uses the same map picker, pre-filled with its
current pin, so you can drag it to correct it.

Files: `apps/distributors/models.py`, `apps/distributors/migrations/0002_distributor_country_and_free_region.py`,
`apps/distributors/views.py`, `apps/distributors/admin.py`,
`apps/analytics/views.py`, `apps/analytics/urls.py`,
`templates/admin/distributors.html`, `templates/distributors.html` (public
page now also shows country when it isn't Uganda).

**Note on the bounding-box check:** it's intentionally coarse (a rectangle
per country) — it exists only to catch gross mistakes like a pin dropped in
the ocean or the wrong country, not to validate exact borders. The live
Nominatim reverse-geocode in the browser is the more precise check, but
since it depends on an external service, the server-side rectangle check is
the one that's guaranteed to run.
