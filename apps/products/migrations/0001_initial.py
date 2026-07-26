from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name='Product',fields=[
        ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
        ('name',models.CharField(max_length=200)),
        ('category',models.CharField(choices=[('pesticide','Pesticide'),('herbicide','Herbicide'),('fungicide','Fungicide'),('other','Other / Agri Input')],max_length=20)),
        ('description',models.TextField(blank=True)),
        ('active_ingredient',models.CharField(blank=True,max_length=300)),
        ('formulation',models.CharField(blank=True,max_length=200)),
        ('crops',models.CharField(blank=True,max_length=300)),
        ('dosage',models.CharField(blank=True,max_length=200)),
        ('packing',models.CharField(blank=True,max_length=200)),
        ('image_url',models.CharField(blank=True,max_length=500)),
        ('image_file',models.ImageField(blank=True,null=True,upload_to='products/')),
        ('created_at',models.DateTimeField(auto_now_add=True)),
    ],options={'ordering':['category','name']})]
