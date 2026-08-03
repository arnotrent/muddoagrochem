from django.db import migrations

FAQS = [
    ('Are your products MAAIF-registered?', 'Yes. All products distributed by MACL are registered with Uganda\'s Ministry of Agriculture, Animal Industry and Fisheries (MAAIF). Certificates available on request.'),
    ('Do you sell wholesale?', 'Absolutely. We supply retail and wholesale. Contact us at +256 772 507582 for bulk pricing and distributor partnerships.'),
    ('How do I choose the right product?', 'Call us or visit our Kampala office. Describe your crop and pest/weed/disease — our team will recommend the right product, dosage and timing.'),
    ('Are your products environmentally safe?', 'All registered products include environmental safety assessments. Follow label instructions: buffer zones, pre-harvest intervals, and proper PPE.'),
    ('Do you deliver upcountry?', 'Products available through our 11-outlet nationwide network. Use our Store Locator. For large bulk orders, direct delivery can be arranged.'),
    ('What is the minimum order?', 'No minimum for retail. For wholesale, minimums vary by product — contact our sales team.'),
    ('How do I report a product problem?', 'Call +256 772 507582 or email muddoagro811@gmail.com. Keep the product, note the batch number, and describe the issue. We investigate all complaints.'),
    ('What is your return policy?', 'Sealed, unused products in original packaging may be returned within 7 days with proof of purchase.'),
]


def seed(apps, schema_editor):
    SiteSettings = apps.get_model('core', 'SiteSettings')
    FAQ = apps.get_model('core', 'FAQ')

    if not SiteSettings.objects.exists():
        SiteSettings.objects.create(pk=1)

    if not FAQ.objects.exists():
        for i, (q, a) in enumerate(FAQS):
            FAQ.objects.create(question=q, answer=a, order=i, active=True)


def unseed(apps, schema_editor):
    pass  # non-destructive on rollback


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_sitesettings_faq'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
