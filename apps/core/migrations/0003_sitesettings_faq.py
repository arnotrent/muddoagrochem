from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_staffprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year_founded', models.CharField(default='2020', max_length=4)),
                ('company_phone', models.CharField(default='+256 772 507582 / 0702-507582', max_length=100)),
                ('company_phone_secondary', models.CharField(blank=True, default='0772 971620 / 0701-971620', max_length=100)),
                ('company_email', models.EmailField(default='muddoagro811@gmail.com', max_length=254)),
                ('company_address', models.CharField(default='Container Village Nakivubo, Equity Bank Basement V013, P.O Box 25240', max_length=300)),
                ('business_hours', models.CharField(default='Monday to Saturday, 8am until 6pm', max_length=200)),
                ('whatsapp_number', models.CharField(default='256772507582', max_length=30)),
                ('facebook_url', models.URLField(blank=True, default='https://facebook.com/p/MUDDO-AGRO-Chemicals-LTD-100063836929481/')),
            ],
            options={'verbose_name': 'Site Settings', 'verbose_name_plural': 'Site Settings'},
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=300)),
                ('answer', models.TextField()),
                ('order', models.PositiveIntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['order', 'id']},
        ),
    ]
