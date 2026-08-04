# This update — real avatar-upload fix, any-format attachments, product photo correction, About page image swap

Drop into your repo at matching paths, then:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

No new migrations this round.

---

## 1. Your security question — is it advisable to let admin edit FAQs/contact details?

Yes, it's both normal and safe, for a specific reason: the risk isn't the
*feature*, it's *who can reach it*. Every Site Content view is wrapped in
`@staff_member_required`, so only accounts with `is_staff=True` can see or
submit that page at all — a random visitor can't reach it no matter what
they try, the same way they can't reach Products or Distributors. It's
form-based, CSRF-protected, and goes through Django's ORM (no raw SQL, so
no injection risk).

The actual thing worth thinking about is **admin account hygiene**, which
is true of this feature exactly as much as it's true of your whole admin
panel already: if your one shared `admin` login is compromised, someone
could change the phone number or email shown on the site — but they could
just as easily delete every product or read every customer enquiry, since
they already have full admin access at that point. The fix for that isn't
restricting Site Content specifically, it's the general practice you
probably already know: a strong, unique admin password, and — if more than
one person manages the site — separate staff accounts per person instead
of one shared login, so changes are attributable. Happy to add per-change
audit logging (who changed what, when) as a small follow-up if you want a
paper trail; I didn't add it by default since it's extra complexity you
may not need for a small team.

## 2. Profile photo upload — the real cause found

You were right that it wasn't a persistence/consistency issue — it was a
genuine upload failure. The code only accepted files ending in
`.png/.jpg/.jpeg/.gif/.webp`; anything else was silently dropped with no
error message, so it looked like nothing happened at all. The most likely
real-world culprit: **iPhones save photos as `.HEIC` by default**, which
wasn't on that list. Fixed two ways:
- Broadened the accepted list (added `.bmp`, `.avif`, `.jfif`).
- **HEIC/HEIF is still not accepted — deliberately** — almost no browser
  except Safari can display it as an image, so accepting it would "work"
  but the photo would look broken everywhere else anyway. Instead of
  silently dropping it, you now get a clear message: *"that photo isn't a
  supported format — please use JPG, PNG, GIF or WEBP"* (with a specific
  note when it detects `.heic`/`.heif`, telling you to export as JPEG
  first — every iPhone's share sheet can do this in two taps).
- Same fix applied to product photo uploads (Add/Edit Product), which had
  the identical silent-drop problem.

## 3. Chat attachments — now genuinely any file format

Removed the `accept="image/*,.pdf,.doc,.docx,.xls,.xlsx"` restriction on
the attach button entirely — it now accepts literally any file. On the
server side, nothing was ever converting or re-encoding attachments — a
`FileField` just stores the exact bytes you upload under their original
extension, so files were always "sent in the same format they're received
in"; that part was already correct. The image-above-text placement inside
each bubble was already in place too (attachment renders before the
caption). What's different now is simply: no format is blocked from being
attached in the first place.

## 4. Product card images — corrected back to fill the frame

Last round's change (object-fit:contain + padding) left visible empty
space around every photo, which wasn't what you wanted — sorry, overcorrected.
Reverted to fill the card edge-to-edge (object-fit:cover, no padding); the
piece that's still removed is the dark gradient overlay that used to wash
the photo out, since that was the actual original complaint. Applied
consistently to the product detail hero image and the quick-view modal too.

## 5. About page — image swap

- Removed the trust/handshake photo from next to the "Who We Are" company
  text — replaced with your new MACL wordmark banner in that spot instead.
- The trust/handshake photo wasn't dropped — it now sits in its own strip
  right below the hero intro ("Farming Uganda depends on, supplied
  honestly."), before "Who We Are" begins, so it's still on the page, just
  not crowding the company-details paragraph.

If this isn't quite the placement you pictured, tell me exactly where
you'd like each image and I'll move them precisely — "next to X" vs "in
its own section above/below Y" are easy to get backwards from text alone,
so no problem adjusting again.
