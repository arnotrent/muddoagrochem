from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name='Distributor',fields=[
        ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
        ('name',models.CharField(max_length=200)),
        ('region',models.CharField(choices=[('Central','Central'),('Eastern','Eastern'),('Northern','Northern'),('Western','Western')],max_length=50)),
        ('district',models.CharField(max_length=100)),('address',models.CharField(blank=True,max_length=300)),
        ('phone',models.CharField(blank=True,max_length=30)),('email',models.EmailField(blank=True,max_length=254)),
        ('lat',models.FloatField(default=0.0)),('lng',models.FloatField(default=0.0)),
        ('created_at',models.DateTimeField(auto_now_add=True)),
    ],options={'ordering':['region','district','name']})]
