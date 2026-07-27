from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributors', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='distributor',
            name='country',
            field=models.CharField(
                choices=[
                    ('Uganda', 'Uganda'), ('Kenya', 'Kenya'), ('Tanzania', 'Tanzania'),
                    ('Rwanda', 'Rwanda'), ('Burundi', 'Burundi'), ('South Sudan', 'South Sudan'),
                    ('DR Congo', 'DR Congo'), ('Other', 'Other'),
                ],
                default='Uganda',
                max_length=100,
            ),
        ),
        migrations.AlterField(
            model_name='distributor',
            name='region',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterModelOptions(
            name='distributor',
            options={'ordering': ['country', 'region', 'district', 'name']},
        ),
    ]
