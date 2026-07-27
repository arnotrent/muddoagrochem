from django.contrib import admin
from .models import Distributor
@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display=['name','country','region','district','phone']
    list_filter=['country','region']
