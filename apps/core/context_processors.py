from django.conf import settings
def global_context(request):
    ctx={'ga_id':getattr(settings,'GA_MEASUREMENT_ID',''),'wa_number':getattr(settings,'WHATSAPP_NUMBER','256772507582'),
         'company_phone':getattr(settings,'COMPANY_PHONE','+256 772 507582'),'company_email':getattr(settings,'COMPANY_EMAIL','kulanju_w@yahoo.com'),
         'unread_count':0,'pending_count':0}
    if request.user.is_authenticated and request.user.is_staff:
        try:
            from apps.messaging.models import Message
            from apps.requests_app.models import SupplyRequest
            ctx['unread_count']=Message.objects.filter(receiver_role='admin',read=False).count()
            ctx['pending_count']=SupplyRequest.objects.filter(status='pending').count()
        except: pass
    if request.user.is_authenticated and not request.user.is_staff:
        try:
            agent=request.user.agent_profile
            from apps.messaging.models import Message
            ctx['agent_unread']=Message.objects.filter(receiver_id=agent.id,receiver_role='agent',read=False).count()
        except: pass
    return ctx
