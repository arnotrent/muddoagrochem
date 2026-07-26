from django.contrib import admin
from .models import Inventory,InventoryLog
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display=['product','stock_qty','reorder_level','unit','last_updated']
    list_filter=['product__category']
@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display=['product','change_qty','reason','changed_by','created_at']
    ordering=['-created_at']
