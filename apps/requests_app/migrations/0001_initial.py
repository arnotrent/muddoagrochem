from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial = True
    dependencies = [('agents','0001_initial')]
    operations = [migrations.CreateModel(name='SupplyRequest',fields=[
        ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
        ('product_name',models.CharField(max_length=200)),('quantity',models.CharField(max_length=100)),
        ('notes',models.TextField(blank=True)),
        ('status',models.CharField(choices=[('pending','Pending'),('approved','Approved'),('denied','Denied')],default='pending',max_length=20)),
        ('admin_response',models.TextField(blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),
        ('updated_at',models.DateTimeField(auto_now=True)),
        ('agent',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='supply_requests',to='agents.agent')),
    ],options={'ordering':['-created_at']})]
