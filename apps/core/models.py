import random, string
from django.db import models

def gen_ref():
    return 'ENQ-'+''.join(random.choices(string.ascii_uppercase+string.digits,k=8))

class ContactRequest(models.Model):
    STATUS=[('new','New'),('pending','Pending'),('resolved','Resolved')]
    SUBJECTS=[('Product Enquiry','Product Enquiry'),('Pricing / Quotation','Pricing / Quotation'),
              ('Wholesale / Bulk Order','Wholesale / Bulk Order'),('Distributor Partnership','Distributor Partnership'),
              ('Technical / Agronomy Advice','Technical / Agronomy Advice'),('General Enquiry','General Enquiry')]
    ref_number=models.CharField(max_length=20,unique=True,default=gen_ref)
    name=models.CharField(max_length=200); email=models.EmailField()
    phone=models.CharField(max_length=30,blank=True)
    subject=models.CharField(max_length=100,choices=SUBJECTS)
    message=models.TextField(); status=models.CharField(max_length=20,choices=STATUS,default='new')
    email_sent=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']
    def __str__(self): return f"[{self.ref_number}] {self.name}"

class NewsletterSubscriber(models.Model):
    email=models.EmailField(unique=True); name=models.CharField(max_length=200,blank=True)
    active=models.BooleanField(default=True); subscribed_at=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.email
