from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name='Agent',fields=[
        ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
        ('phone',models.CharField(blank=True,max_length=30)),('region',models.CharField(blank=True,max_length=100)),
        ('district',models.CharField(blank=True,max_length=100)),
        ('status',models.CharField(choices=[('active','Active'),('inactive','Inactive')],default='active',max_length=20)),
        ('last_seen',models.DateTimeField(blank=True,null=True)),('created_at',models.DateTimeField(auto_now_add=True)),
        ('user',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='agent_profile',to=settings.AUTH_USER_MODEL)),
    ],options={'ordering':['user__first_name']})]
