from django.contrib import admin
from .models import ContactRequest,NewsletterSubscriber,StaffProfile
@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display=['ref_number','name','email','subject','status','created_at']
    list_filter=['status']; ordering=['-created_at']
@admin.register(NewsletterSubscriber)
class NewsletterAdmin(admin.ModelAdmin):
    list_display=['email','name','active','subscribed_at']
@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display=['user','display_name']
