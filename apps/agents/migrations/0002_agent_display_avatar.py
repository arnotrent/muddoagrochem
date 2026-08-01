from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='display_name',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='agent',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/agents/'),
        ),
    ]
