from django.contrib import admin
from .models import Distributor
@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display=['name','region','district','phone']
    list_filter=['region']
