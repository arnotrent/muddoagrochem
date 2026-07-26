from django.contrib import admin
from .models import Agent
@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display=['name','region','district','status','last_seen']
    list_filter=['status','region']
