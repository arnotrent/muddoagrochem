from django.db import migrations, models
import django.db.models.deletion
class Migration(migrations.Migration):
    initial = True
    dependencies = [('products','0001_initial')]
    operations = [
        migrations.CreateModel(name='Inventory',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('stock_qty',models.IntegerField(default=0)),('reorder_level',models.IntegerField(default=10)),
            ('unit',models.CharField(default='units',max_length=50)),('last_updated',models.DateTimeField(auto_now=True)),
            ('product',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='inventory',to='products.product')),
        ],options={'verbose_name_plural':'Inventories'}),
        migrations.CreateModel(name='InventoryLog',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('change_qty',models.IntegerField()),('reason',models.CharField(blank=True,max_length=300)),
            ('changed_by',models.CharField(blank=True,max_length=100)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('product',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='logs',to='products.product')),
        ],options={'ordering':['-created_at']}),
    ]
