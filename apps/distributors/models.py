from django.db import models

class Distributor(models.Model):
    REGIONS=[('Central','Central'),('Eastern','Eastern'),('Northern','Northern'),('Western','Western')]
    name=models.CharField(max_length=200); region=models.CharField(max_length=50,choices=REGIONS)
    district=models.CharField(max_length=100); address=models.CharField(max_length=300,blank=True)
    phone=models.CharField(max_length=30,blank=True); email=models.EmailField(blank=True)
    lat=models.FloatField(default=0.0); lng=models.FloatField(default=0.0)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['region','district','name']
    def __str__(self): return f"{self.name} ({self.region})"
