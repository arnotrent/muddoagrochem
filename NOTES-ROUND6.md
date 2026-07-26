# Round 6 notes

## THE CRASH — root cause and fix
Your traceback was exact and made this easy to diagnose:
```
django.template.exceptions.TemplateSyntaxError: 'icons' is not a registered tag library.
Must be one of: admin_list admin_modify admin_urls cache i18n l10n log muddo_filters static tz
```
`muddo_filters` (same app, same folder) loaded fine — `icons` didn't. Django's
template-library loader silently swallows an `ImportError` when scanning
`templatetags/` (`except ImportError: continue`), so if a templatetags file
is missing or fails to import, you get no startup error at all — it just
isn't registered, and every `{% load icons %}` blows up at request time.
I tested my copy of `apps/core/templatetags/icons.py` fresh (clean import,
no errors) — so the most likely explanation is that this file didn't
actually make it into your deployed repo. This has been a recurring pattern
across rounds: copying individual changed files into your existing repo is
where things have been getting dropped. **Please replace your entire repo
contents with this zip rather than merging file-by-file** — that removes
this whole class of bug going forward.

I also reproduced your exact failure locally this time before shipping:
ran with `DEBUG=False` and a real `collectstatic` manifest (matching
Render's actual conditions, not just my dev-mode tests), and specifically
hit a nonexistent URL to trigger the 404 handler → `base.html` → `{% load
icons %}` path — the precise chain from your traceback. All green.

## Products removed (discontinued, not actually stocked)
MD Ametryn 500SC, Weed IT 75.7 XL, Top Fenos 50EC, Copper Oxychloride 850WP
— removed from `seed_data.py`. Catalogue is now 16 products. If these are
still sitting in your live database, delete them once via Admin → Products
(trash icon) since `seed_data` only adds/updates, it never removes rows
that are no longer in the list.

## Top-Laxly products — left alone, as asked
Confirmed: TOP-LAXLY M 72WP, MD TOP LAXLYN 72WP, and TOPLAXLY 72WP are kept
exactly as three separate products, untouched. No merge, no dedupe applied
to them — noted and respected.

## Urea & Foliar Boost — real images now
- **Urea 46%N** → the fertilizer granule bag photo you provided earlier
  (`hero_fertilizers.jpg` source).
- **Foliar Boost** → the hand-applying-to-seedling "plant application"
  photo (`hero_home.jpg` source). Worth flagging honestly: this specific
  source photo is only 192×128px — quite small — so it will look soft
  blown up to card size. Used it because you asked for it specifically;
  send a higher-resolution version whenever you have one and it's a
  one-file swap.

