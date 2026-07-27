# Round 7 notes

## FAQ accordion — fixed
The About page FAQ toggle broke as a side effect of last round's Font
Awesome → SVG icon conversion. `toggleFaq()` was looking for the chevron
via `btn.querySelector('i')` — but there are no `<i>` tags left anywhere
on the site now, they're all `<svg class="icon ...">`. That lookup
returned `null`, and the next line tried to set `.style.transform` on
it, throwing a JS error before the code ever reached the line that
actually expands the answer panel. Fixed to query `.icon` instead, with
null-safety added so a missing icon can never silently break the whole
handler again.

## Mobile layout fixes
Two real responsive bugs, both from grids styled with a plain inline
`style="display:grid;grid-template-columns:1fr 1fr"` and no class for
`responsive.css` to actually target on narrow screens:
- **Contact page**: the two-column layout (info cards / message form)
  wasn't collapsing on mobile — this is exactly what your screenshot
  showed overlapping. Added a `contact-grid` class so the existing
  mobile rule can reach it.
- **About page "Who We Are"** and **homepage "Field-Tested"** sections
  (photo + text side by side) had the same problem. Added a new reusable
  `.stack-mobile` utility class and applied it to both, plus the contact
  form's Name/Phone field pair.

## Products
- Removed **TOPLAXLY 72WP** — confirmed as the repeat you meant (same
  product as TOP-LAXLY M / MD Top Laxlyn, just different packaging).
- Removed **UREA 46%N** — not an actual Muddo product.
- Catalogue is now 14 products.

## Email
Every reference to `kulanju_w@yahoo.com` — templates, views, seed data,
and Django's own settings (`COMPANY_EMAIL`, `DEFAULT_FROM_EMAIL`,
`EMAIL_HOST_USER` default) — now points to `muddoagro811@gmail.com`.

## New imagery
- **Pesticides hero** → the aphid/beetle/whitefly pest collage you sent.
- **Herbicides hero** → the backpack sprayer field-application photo
  (much higher resolution than what was there before, 1672×941).
- **Fungicides hero** → the "Healthy vs Affected" tomato comparison
  image — this is the "tomato merged images" you meant, now front and
  center on exactly the right page.
- **Homepage "Field-Tested" section** → tomato blight leaf (the problem)
  paired with healthy greenhouse tomatoes (the result).
- **About page side photo** → swapped off the pesticide image (wrong
  context) onto the healthy greenhouse tomatoes photo instead.
- **Contact page** → now has a real photo hero instead of a flat color.
- **Admin panel** → given its own distinct branding using the "MACL
  Admin" logo you sent, instead of reusing the main site logo in the
  sidebar. Public site logo is untouched everywhere else.

Not used: the two generic "Contact Us" / "About Us" stock-graphic images
(icons-on-gradient / neon-space style) — they clash with the site's
clean grayscale-and-blue look and read as generic stock art rather than
real photography, so I left them out rather than use them just because
they were sent. Happy to reconsider if you specifically want one of them
somewhere.
