from django.contrib import admin
from .models import SupplyRequest
@admin.register(SupplyRequest)
class SupplyRequestAdmin(admin.ModelAdmin):
    list_display=['agent','product_name','quantity','status','created_at']
    list_filter=['status']; ordering=['-created_at']
