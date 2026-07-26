"""
Inline SVG icon system.

Why this exists: Font Awesome (and any icon font) renders glyphs via a
webfont mapped to private-use Unicode codepoints. If that font fails to
load — CDN blocked, offline, slow network, strict CSP — the browser falls
back to its default font for those codepoints, which on many systems means
generic emoji-style glyphs instead of the intended icon. Inline SVG has no
such failure mode: the vector paths are part of the HTML itself.

Usage in a template:
    {% load icons %}
    {% icon "envelope" %}
    {% icon "truck" style="color:var(--accent-blue);margin-right:6px" %}
    {% icon "check-circle" css_class="my-extra-class" size="20" %}

Every icon defaults to width/height="1em" so it scales with the
surrounding font-size exactly like an icon-font glyph did.
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# name -> (inner_svg_markup, mode)
# mode "stroke" -> outline icon, fill:none stroke:currentColor
# mode "fill"   -> solid icon (brand logos etc.), fill:currentColor
ICONS = {
    # ── communication / contact ──────────────────────────────
    "envelope": ('<path d="M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/><polyline points="22 6 12 13 2 6"/>', "stroke"),
    "phone": ('<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>', "stroke"),
    "comments": ('<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>', "stroke"),
    "comment": ('<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>', "stroke"),
    "paper-plane": ('<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>', "stroke"),
    "reply": ('<polyline points="9 14 4 9 9 4"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/>', "stroke"),
    "headset": ('<path d="M3 14v-2a9 9 0 0 1 18 0v2"/><path d="M21 14v4a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3z"/><path d="M3 14v4a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/>', "stroke"),

    # ── nav / actions ─────────────────────────────────────────
    "search": ('<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>', "stroke"),
    "times": ('<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>', "stroke"),
    "times-circle": ('<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>', "stroke"),
    "check": ('<polyline points="20 6 9 17 4 12"/>', "stroke"),
    "check-circle": ('<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>', "stroke"),
    "check-double": ('<polyline points="1 13 5 17 11 9"/><polyline points="7 13 11 17 21 5"/>', "stroke"),
    "plus": ('<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>', "stroke"),
    "plus-circle": ('<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>', "stroke"),
    "chevron-down": ('<polyline points="6 9 12 15 18 9"/>', "stroke"),
    "arrow-left": ('<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>', "stroke"),
    "arrow-right": ('<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>', "stroke"),
    "arrow-up": ('<line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>', "stroke"),
    "sign-in-alt": ('<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/>', "stroke"),
    "sign-out-alt": ('<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>', "stroke"),
    "eye": ('<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>', "stroke"),
    "eye-slash": ('<path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a21.86 21.86 0 0 1 5.06-6.94M9.9 4.24A10.94 10.94 0 0 1 12 4c7 0 11 8 11 8a21.8 21.8 0 0 1-3.22 4.6"/><path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>', "stroke"),
    "info-circle": ('<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>', "stroke"),
    "exclamation-circle": ('<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>', "stroke"),
    "exclamation-triangle": ('<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>', "stroke"),
    "question-circle": ('<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>', "stroke"),

    # ── catalogue / commerce ──────────────────────────────────
    "bug": ('<circle cx="12" cy="14" r="6"/><path d="M12 8V5"/><path d="M9 5l1.5 2M15 5l-1.5 2"/><path d="M6 14H3M21 14h-3"/><path d="M7.5 10.3 5.6 8.4M16.5 10.3l1.9-1.9"/><path d="M7.5 17.7l-1.9 1.9M16.5 17.7l1.9 1.9"/>', "stroke"),
    "seedling": ('<path d="M12 21V10"/><path d="M12 10C12 6 9 4 5 4c0 4 2 7 7 7"/><path d="M12 10c0-4 3-6 7-6 0 4-2 7-7 7"/>', "stroke"),
    "flask": ('<path d="M9 2v6.34a2 2 0 0 1-.4 1.2L4.4 16.8A3 3 0 0 0 7 21h10a3 3 0 0 0 2.6-4.2l-4.2-7.26a2 2 0 0 1-.4-1.2V2"/><path d="M8 2h8"/><path d="M8.5 12h7"/>', "stroke"),
    "microscope": ('<path d="M9 2v6.34a2 2 0 0 1-.4 1.2L4.4 16.8A3 3 0 0 0 7 21h10a3 3 0 0 0 2.6-4.2l-4.2-7.26a2 2 0 0 1-.4-1.2V2"/><path d="M8 2h8"/><path d="M8.5 12h7"/>', "stroke"),
    "boxes": ('<path d="M21 8 12 3 3 8v8l9 5 9-5V8z"/><path d="M3 8l9 5 9-5"/><line x1="12" y1="13" x2="12" y2="21"/>', "stroke"),
    "box": ('<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>', "stroke"),
    "box-open": ('<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>', "stroke"),
    "leaf": ('<path d="M5 21c9 0 13-6 13-14V5h-2C10 5 4 9 4 18v3z"/><path d="M4 21l6-6"/>', "stroke"),
    "balance-scale": ('<line x1="12" y1="3" x2="12" y2="21"/><path d="M5 7l-3 6a3 3 0 0 0 6 0l-3-6z"/><path d="M19 7l-3 6a3 3 0 0 0 6 0l-3-6z"/><line x1="5" y1="7" x2="19" y2="7"/><line x1="9" y1="21" x2="15" y2="21"/>', "stroke"),
    "store": ('<path d="M3 9l1-5h16l1 5"/><path d="M3 9a2 2 0 0 0 4 0 2 2 0 0 0 4 0 2 2 0 0 0 4 0 2 2 0 0 0 4 0"/><path d="M4 9v10a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1V9"/><path d="M9 21v-6h6v6"/>', "stroke"),
    "truck": ('<rect x="1" y="3" width="15" height="13"/><path d="M16 8h4l3 3v5h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>', "stroke"),
    "star": ('<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>', "stroke"),
    "award": ('<circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>', "stroke"),
    "certificate": ('<circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>', "stroke"),
    "directions": ('<polygon points="3 11 22 2 13 21 11 13 3 11"/>', "stroke"),
    "map-marker-alt": ('<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>', "stroke"),

    # ── people / org ──────────────────────────────────────────
    "user": ('<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>', "stroke"),
    "user-tie": ('<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>', "stroke"),
    "user-plus": ('<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/>', "stroke"),
    "users": ('<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>', "stroke"),
    "building": ('<rect x="4" y="2" width="16" height="20" rx="1"/><path d="M9 22v-4h6v4"/><line x1="8" y1="6" x2="8.01" y2="6"/><line x1="12" y1="6" x2="12.01" y2="6"/><line x1="16" y1="6" x2="16.01" y2="6"/><line x1="8" y1="10" x2="8.01" y2="10"/><line x1="12" y1="10" x2="12.01" y2="10"/><line x1="16" y1="10" x2="16.01" y2="10"/><line x1="8" y1="14" x2="8.01" y2="14"/><line x1="12" y1="14" x2="12.01" y2="14"/><line x1="16" y1="14" x2="16.01" y2="14"/>', "stroke"),
    "handshake": ('<path d="M8 14l2.5 2.5a1.5 1.5 0 0 0 2.12 0 1.5 1.5 0 0 0 0-2.12L11 12.5"/><path d="M11 12.5 8.62 10.1a1.5 1.5 0 0 0-2.12 0l-.7.71a1.5 1.5 0 0 0 0 2.12L8 15.14"/><path d="M13 13.5l1.5 1.5a1.5 1.5 0 0 0 2.12 0 1.5 1.5 0 0 0 0-2.12L14.5 10.5"/><path d="M2 12l4-4 4.5 4.5"/><path d="M22 12l-4-4-6 6"/>', "stroke"),
    "shield-alt": ('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>', "stroke"),
    "map-marked-alt": ('<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>', "stroke"),
    "clock": ('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>', "stroke"),

    # ── layout / misc UI ──────────────────────────────────────
    "cog": ('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>', "stroke"),
    "lock": ('<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>', "stroke"),
    "key": ('<path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>', "stroke"),
    "globe": ('<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>', "stroke"),
    "list": ('<line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>', "stroke"),
    "th-large": ('<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>', "stroke"),
    "table": ('<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>', "stroke"),
    "layer-group": ('<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>', "stroke"),
    "home": ('<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>', "stroke"),
    "history": ('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>', "stroke"),
    "tachometer-alt": ('<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>', "stroke"),
    "bolt": ('<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>', "stroke"),
    "lightbulb": ('<path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.2 1 2.3h6c0-1.1.4-1.8 1-2.3A7 7 0 0 0 12 2z"/>', "stroke"),
    "moon": ('<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>', "stroke"),
    "sun": ('<circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>', "stroke"),

    # ── admin / crud ──────────────────────────────────────────
    "edit": ('<path d="M17 3a2.83 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>', "stroke"),
    "trash": ('<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>', "stroke"),
    "save": ('<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>', "stroke"),
    "upload": ('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>', "stroke"),
    "print": ('<polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>', "stroke"),
    "pause": ('<rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>', "stroke"),
    "play": ('<polygon points="5 3 19 12 5 21 5 3"/>', "stroke"),
    "file-pdf": ('<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>', "stroke"),

    # ── brand (filled) ────────────────────────────────────────
    "whatsapp": ('<path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2zm0 18.13h-.01a8.2 8.2 0 0 1-4.19-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.2 8.2 0 0 1-1.26-4.37c0-4.54 3.7-8.24 8.25-8.24 2.2 0 4.27.86 5.83 2.42a8.18 8.18 0 0 1 2.41 5.83c0 4.55-3.7 8.24-8.24 8.24zm4.52-6.16c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.13-.17.24-.64.81-.78.97-.14.17-.29.19-.53.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.24-.02-.37.11-.5.11-.11.25-.29.37-.43.12-.15.16-.25.25-.42.08-.17.04-.31-.02-.43-.06-.12-.56-1.35-.77-1.85-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.43.06-.66.31-.23.24-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.57.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.67-1.18.21-.58.21-1.08.14-1.18-.06-.11-.23-.17-.48-.29z"/>', "fill"),
    "facebook-f": ('<path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.77-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.78l-.44 2.89h-2.34v6.99A10 10 0 0 0 22 12z"/>', "fill"),
}

# icons that are just aliases of another icon's shape
ICONS["fungicide-flask"] = ICONS["flask"]
ICONS["facebook"] = ICONS["facebook-f"]
ICONS["envelope-open"] = ICONS["envelope"]


def _render(name, size, style, css_class, spin):
    entry = ICONS.get(name)
    if not entry:
        # Unknown icon name → render a small neutral dot rather than
        # nothing, so a typo doesn't silently blank out a whole button.
        inner, mode = '<circle cx="12" cy="12" r="3"/>', "stroke"
    else:
        inner, mode = entry

    if mode == "fill":
        fill, stroke = "currentColor", "none"
        extra_attrs = ""
    else:
        fill, stroke = "none", "currentColor"
        extra_attrs = ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'

    dim = size or "1em"
    classes = f"icon icon-{name}"
    if spin:
        classes += " icon-spin"
    if css_class:
        classes += f" {css_class}"

    style_attr = f' style="{style}"' if style else ""

    return mark_safe(
        f'<svg class="{classes}" width="{dim}" height="{dim}" viewBox="0 0 24 24" '
        f'fill="{fill}" stroke="{stroke}"{extra_attrs}{style_attr} aria-hidden="true" focusable="false">{inner}</svg>'
    )


@register.simple_tag
def icon(name, size=None, style="", css_class="", spin=False):
    return _render(name, size, style, css_class, spin)
