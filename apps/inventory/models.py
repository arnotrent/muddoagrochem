from django.db import models

class Inventory(models.Model):
    product       = models.OneToOneField('products.Product',on_delete=models.CASCADE,related_name='inventory')
    stock_qty     = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    unit          = models.CharField(max_length=50,default='units')
    last_updated  = models.DateTimeField(auto_now=True)
    class Meta: verbose_name_plural='Inventories'
    def __str__(self): return f"{self.product.name} — {self.stock_qty}"
    @property
    def is_low(self): return self.stock_qty<=self.reorder_level
    @property
    def status(self):
        if self.stock_qty==0: return 'out'
        if self.is_low: return 'low'
        return 'in'

class InventoryLog(models.Model):
    product    = models.ForeignKey('products.Product',on_delete=models.CASCADE,related_name='logs')
    change_qty = models.IntegerField()
    reason     = models.CharField(max_length=300,blank=True)
    changed_by = models.CharField(max_length=100,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']
