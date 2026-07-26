from django.db import models
from django.urls import reverse

CATS = [('pesticide','Pesticide'),('herbicide','Herbicide'),('fungicide','Fungicide'),('other','Other / Agri Input')]

class Product(models.Model):
    name              = models.CharField(max_length=200)
    category          = models.CharField(max_length=20, choices=CATS)
    description       = models.TextField(blank=True)
    active_ingredient = models.CharField(max_length=300, blank=True)
    formulation       = models.CharField(max_length=200, blank=True)
    crops             = models.CharField(max_length=300, blank=True)
    dosage            = models.CharField(max_length=200, blank=True)
    packing           = models.CharField(max_length=200, blank=True)
    image_url         = models.CharField(max_length=500, blank=True)
    image_file        = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['category','name']
    def __str__(self): return f"{self.name} ({self.get_category_display()})"
    def get_absolute_url(self): return reverse('product_detail',args=[self.pk])
    @property
    def display_image(self):
        if self.image_file: return self.image_file.url
        if self.image_url:  return self.image_url
        return '/static/images/products_all.jpg'
    @property
    def stock_qty(self):
        try: return self.inventory.stock_qty
        except: return 0
    @property
    def stock_status(self):
        q=self.stock_qty
        if q==0: return 'out'
        if q<=10: return 'low'
        return 'in'
