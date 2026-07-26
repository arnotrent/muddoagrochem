from django.db import migrations, models
import apps.core.models
class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name='ContactRequest',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('ref_number',models.CharField(default=apps.core.models.gen_ref,max_length=20,unique=True)),
            ('name',models.CharField(max_length=200)),('email',models.EmailField(max_length=254)),
            ('phone',models.CharField(blank=True,max_length=30)),
            ('subject',models.CharField(choices=[('Product Enquiry','Product Enquiry'),('Pricing / Quotation','Pricing / Quotation'),('Wholesale / Bulk Order','Wholesale / Bulk Order'),('Distributor Partnership','Distributor Partnership'),('Technical / Agronomy Advice','Technical / Agronomy Advice'),('General Enquiry','General Enquiry')],max_length=100)),
            ('message',models.TextField()),('status',models.CharField(choices=[('new','New'),('pending','Pending'),('resolved','Resolved')],default='new',max_length=20)),
            ('email_sent',models.BooleanField(default=False)),('created_at',models.DateTimeField(auto_now_add=True)),
        ],options={'ordering':['-created_at']}),
        migrations.CreateModel(name='NewsletterSubscriber',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('email',models.EmailField(max_length=254,unique=True)),('name',models.CharField(blank=True,max_length=200)),
            ('active',models.BooleanField(default=True)),('subscribed_at',models.DateTimeField(auto_now_add=True)),
        ]),
    ]
