from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name='Message',fields=[
        ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
        ('sender_id',models.IntegerField()),('sender_role',models.CharField(choices=[('admin','Admin'),('agent','Agent')],max_length=10)),
        ('receiver_id',models.IntegerField()),('receiver_role',models.CharField(choices=[('admin','Admin'),('agent','Agent')],max_length=10)),
        ('content',models.TextField()),('read',models.BooleanField(default=False)),
        ('created_at',models.DateTimeField(auto_now_add=True)),
    ],options={'ordering':['created_at']})]
