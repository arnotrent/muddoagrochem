from django.core.management.base import BaseCommand
from django.db import transaction
from apps.products.models import Product
from apps.inventory.models import Inventory


class Command(BaseCommand):
    help = 'Finds products that share the same name (case-insensitive) and merges them into one row.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Actually delete the duplicates (default is a dry run).')

    def handle(self, *args, **opts):
        apply = opts['apply']
        seen = {}
        for p in Product.objects.all().order_by('id'):
            key = p.name.strip().lower()
            seen.setdefault(key, []).append(p)

        groups = {k: v for k, v in seen.items() if len(v) > 1}
        if not groups:
            self.stdout.write(self.style.SUCCESS('No duplicate products found — nothing to do.'))
            return

        total_removed = 0
        for key, dupes in groups.items():
            # Prefer: has a real uploaded photo > has an image_url > has a description > oldest row
            def score(p):
                return (
                    1 if p.image_file else 0,
                    1 if p.image_url else 0,
                    1 if p.description else 0,
                    -p.id,  # earlier id wins ties (created first)
                )
            dupes_sorted = sorted(dupes, key=score, reverse=True)
            keeper, extras = dupes_sorted[0], dupes_sorted[1:]

            combined_stock = 0
            for e in [keeper] + extras:
                combined_stock += e.stock_qty

            self.stdout.write(f'\n"{dupes[0].name}" — {len(dupes)} copies found:')
            self.stdout.write(f'  KEEP  id={keeper.id}  stock={keeper.stock_qty}  photo={"yes" if (keeper.image_file or keeper.image_url) else "no"}')
            for e in extras:
                self.stdout.write(f'  REMOVE id={e.id}  stock={e.stock_qty}  photo={"yes" if (e.image_file or e.image_url) else "no"}')

            if apply:
                with transaction.atomic():
                    inv, _ = Inventory.objects.get_or_create(product=keeper, defaults={'stock_qty': 0})
                    inv.stock_qty = combined_stock
                    inv.save(update_fields=['stock_qty'])
                    for e in extras:
                        e.delete()  # cascades to that row's own Inventory/logs
                total_removed += len(extras)

        if apply:
            self.stdout.write(self.style.SUCCESS(f'\nDone — removed {total_removed} duplicate row(s), stock quantities combined into the kept product.'))
        else:
            self.stdout.write(self.style.WARNING('\nDry run only — re-run with --apply to actually merge/delete these.'))
