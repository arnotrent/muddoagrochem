import time, json, urllib.request, urllib.parse
from django.core.management.base import BaseCommand
from apps.distributors.models import Distributor

COUNTRY_ISO = {
    'Uganda': 'ug', 'Kenya': 'ke', 'Tanzania': 'tz', 'Rwanda': 'rw',
    'Burundi': 'bi', 'South Sudan': 'ss', 'DR Congo': 'cd',
}


class Command(BaseCommand):
    help = (
        "Reverse-geocodes every saved distributor location (via free OpenStreetMap "
        "Nominatim) and flags any that fall outside their assigned country/district, "
        "or land in open water. Requires outbound internet access — run this on your "
        "deployed server (Render shell), not in an offline dev environment."
    )

    def handle(self, *args, **opts):
        dists = Distributor.objects.all()
        if not dists.exists():
            self.stdout.write('No distributors saved yet — nothing to check.')
            return

        flagged = 0
        total = dists.count()
        for d in dists:
            if not d.lat or not d.lng:
                self.stdout.write(self.style.WARNING(f'⚠ {d.name}: no coordinates saved at all.'))
                flagged += 1
                continue

            url = 'https://nominatim.openstreetmap.org/reverse?' + urllib.parse.urlencode({
                'format': 'json', 'lat': d.lat, 'lon': d.lng, 'zoom': 14, 'addressdetails': 1,
            })
            req = urllib.request.Request(url, headers={
                'User-Agent': 'MuddoAgroLocationCheck/1.0 (muddoagro811@gmail.com)'
            })
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ {d.name}: could not verify right now ({e}).'))
                flagged += 1
                time.sleep(1)
                continue

            if not data or 'error' in data or 'address' not in data:
                self.stdout.write(self.style.ERROR(
                    f'✗ {d.name}: no land found at ({d.lat}, {d.lng}) — likely over water, '
                    f'a lake/swamp, or an unmapped area. Reposition this pin.'
                ))
                flagged += 1
            else:
                addr = data['address']
                got_iso = (addr.get('country_code') or '').lower()
                wanted_iso = COUNTRY_ISO.get(d.country, '')
                display = data.get('display_name', '')
                district_hit = (d.district or '').strip().lower() in display.lower()

                if wanted_iso and got_iso and got_iso != wanted_iso:
                    self.stdout.write(self.style.ERROR(
                        f'✗ {d.name}: pin resolves to {addr.get("country", got_iso)}, not {d.country}. ({display})'
                    ))
                    flagged += 1
                elif not district_hit:
                    self.stdout.write(self.style.WARNING(
                        f'~ {d.name}: pin is in {d.country}, but "{d.district}" doesn\'t appear in the '
                        f'resolved address — worth double-checking it\'s the right town. ({display[:100]})'
                    ))
                    flagged += 1
                else:
                    self.stdout.write(self.style.SUCCESS(f'✓ {d.name}: OK — {display[:90]}'))

            time.sleep(1)  # Nominatim usage policy: max 1 request/second

        self.stdout.write(f'\nChecked {total} outlet(s) — {flagged} flagged for review.')
