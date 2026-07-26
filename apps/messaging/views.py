import json
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from apps.messaging.models import Message
from apps.agents.models import Agent

@staff_member_required
def admin_chat(request):
    agents=Agent.objects.filter(status='active').select_related('user')
    unread_map={}
    for m in Message.objects.filter(receiver_role='admin',read=False):
        k=str(m.sender_id); unread_map[k]=unread_map.get(k,0)+1
    return render(request,'admin/chat.html',{'agents':agents,'unread_map':unread_map})

def _id(user):
    if user.is_staff: return user.id,'admin'
    try: return user.agent_profile.id,'agent'
    except: return user.id,'agent'

def _bump(user):
    if not user.is_staff:
        try: user.agent_profile.last_seen=timezone.now(); user.agent_profile.save(update_fields=['last_seen'])
        except: pass

@login_required
def api_messages(request):
    _bump(request.user)
    with_id=int(request.GET.get('with_id',0)); with_role=request.GET.get('with_role','agent')
    after=int(request.GET.get('after',0)); my_id,my_role=_id(request.user)
    msgs=(Message.objects.filter(id__gt=after,sender_id=my_id,sender_role=my_role,receiver_id=with_id,receiver_role=with_role)|
          Message.objects.filter(id__gt=after,sender_id=with_id,sender_role=with_role,receiver_id=my_id,receiver_role=my_role)).order_by('id')[:100]
    return JsonResponse({'messages':[{'id':m.id,'sender_id':m.sender_id,'sender_role':m.sender_role,'receiver_id':m.receiver_id,'receiver_role':m.receiver_role,'content':m.content,'read':m.read,'created_at':m.created_at.isoformat()} for m in msgs]})

@login_required
@require_POST
def api_send(request):
    _bump(request.user)
    try: data=json.loads(request.body)
    except: return JsonResponse({'error':'Invalid JSON'},status=400)
    to_id=data.get('to_id'); to_role=data.get('to_role','agent'); content=(data.get('content') or '').strip()
    if not content or not to_id: return JsonResponse({'error':'Missing fields'},status=400)
    my_id,my_role=_id(request.user)
    m=Message.objects.create(sender_id=my_id,sender_role=my_role,receiver_id=to_id,receiver_role=to_role,content=content)
    return JsonResponse({'message':{'id':m.id,'sender_id':m.sender_id,'sender_role':m.sender_role,'receiver_id':m.receiver_id,'receiver_role':m.receiver_role,'content':m.content,'read':m.read,'created_at':m.created_at.isoformat()}})

@login_required
def api_unread(request):
    my_id,my_role=_id(request.user)
    msgs=Message.objects.filter(receiver_id=my_id,receiver_role=my_role,read=False)
    per={}
    for m in msgs:
        k=f'{m.sender_id}_{m.sender_role}'; per[k]=per.get(k,0)+1
    return JsonResponse({'total':msgs.count(),'per_contact':per})

@login_required
@require_POST
def api_mark_read(request):
    try: data=json.loads(request.body)
    except: return JsonResponse({'error':'bad json'},status=400)
    my_id,my_role=_id(request.user)
    Message.objects.filter(sender_id=data.get('from_id'),sender_role=data.get('from_role'),receiver_id=my_id,receiver_role=my_role).update(read=True)
    return JsonResponse({'ok':True})
