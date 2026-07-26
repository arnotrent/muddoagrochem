from django.contrib import admin
from .models import Message
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display=['sender_role','sender_id','receiver_role','receiver_id','read','created_at']
    list_filter=['sender_role','read']
