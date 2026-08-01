from django.conf import settings
def global_context(request):
    ctx={'ga_id':getattr(settings,'GA_MEASUREMENT_ID',''),'wa_number':getattr(settings,'WHATSAPP_NUMBER','256772507582'),
         'company_phone':getattr(settings,'COMPANY_PHONE','+256 772 507582'),'company_email':getattr(settings,'COMPANY_EMAIL','muddoagro811@gmail.com'),
         'unread_count':0,'pending_count':0}
    if request.user.is_authenticated and request.user.is_staff:
        try:
            from apps.messaging.models import Message
            from apps.requests_app.models import SupplyRequest
            direct_unread = Message.objects.filter(receiver_role='admin',read=False,is_broadcast=False).count()
            team_unread = Message.objects.filter(is_broadcast=True,read=False).exclude(sender_id=request.user.id,sender_role='admin').count()
            ctx['unread_count'] = direct_unread + team_unread
            ctx['pending_count']=SupplyRequest.objects.filter(status='pending').count()
        except: pass
    if request.user.is_authenticated and not request.user.is_staff:
        try:
            agent=request.user.agent_profile
            from apps.messaging.models import Message
            direct_unread = Message.objects.filter(receiver_id=agent.id,receiver_role='agent',read=False,is_broadcast=False).count()
            team_unread = Message.objects.filter(is_broadcast=True,read=False).exclude(sender_id=agent.id,sender_role='agent').count()
            ctx['agent_unread'] = direct_unread + team_unread
        except: pass
    return ctx
