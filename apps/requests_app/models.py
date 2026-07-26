from django.db import models

class SupplyRequest(models.Model):
    STATUS=[('pending','Pending'),('approved','Approved'),('denied','Denied')]
    agent          = models.ForeignKey('agents.Agent',on_delete=models.CASCADE,related_name='supply_requests')
    product_name   = models.CharField(max_length=200)
    quantity       = models.CharField(max_length=100)
    notes          = models.TextField(blank=True)
    status         = models.CharField(max_length=20,choices=STATUS,default='pending')
    admin_response = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    class Meta: ordering=['-created_at']
    def __str__(self): return f"{self.agent} — {self.product_name}"
