import json
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from apps.messaging.models import Message
from apps.agents.models import Agent


@staff_member_required
def admin_chat(request):
    agents = list(Agent.objects.filter(status='active').select_related('user'))

    unread_map = {}
    for m in Message.objects.filter(receiver_role='admin', read=False, is_broadcast=False):
        k = str(m.sender_id); unread_map[k] = unread_map.get(k, 0) + 1

    # Last direct (non-broadcast) message per agent, for the recent-chats preview.
    last_by_agent = {}
    dm_msgs = Message.objects.filter(is_broadcast=False).filter(
        Q(sender_role='agent') | Q(receiver_role='agent')
    ).order_by('-id')
    for m in dm_msgs:
        aid = m.sender_id if m.sender_role == 'agent' else m.receiver_id
        if aid not in last_by_agent:
            last_by_agent[aid] = m

    for a in agents:
        m = last_by_agent.get(a.id)
        a.last_message_preview = (m.content[:46] + ('…' if len(m.content) > 46 else '')) if m else ''
        a.last_message_time = m.created_at if m else None
        a.last_message_mine = bool(m and m.sender_role == 'admin')
        a.unread_from = unread_map.get(str(a.id), 0)

    agents.sort(key=lambda a: (a.unread_from == 0, -(a.last_message_time.timestamp() if a.last_message_time else 0)))

    last_broadcast = Message.objects.filter(is_broadcast=True, sender_role='admin').order_by('-id').first()

    return render(request, 'admin/chat.html', {
        'agents': agents,
        'unread_map': unread_map,
        'last_broadcast': last_broadcast,
    })

def _id(user):
    if user.is_staff: return user.id,'admin'
    try: return user.agent_profile.id,'agent'
    except: return user.id,'agent'

def _bump(user):
    if not user.is_staff:
        try: user.agent_profile.last_seen=timezone.now(); user.agent_profile.save(update_fields=['last_seen'])
        except: pass

def _serialize(m):
    return {
        'id': m.id, 'sender_id': m.sender_id, 'sender_role': m.sender_role,
        'receiver_id': m.receiver_id, 'receiver_role': m.receiver_role,
        'content': m.content, 'read': m.read, 'is_broadcast': m.is_broadcast,
        'created_at': m.created_at.isoformat(),
    }

@login_required
def api_messages(request):
    _bump(request.user)
    with_role = request.GET.get('with_role', 'agent')
    after = int(request.GET.get('after', 0) or 0)
    my_id, my_role = _id(request.user)

    if with_role == 'broadcast':
        # Admin viewing the "All Agents" thread.
        msgs = Message.objects.filter(is_broadcast=True, id__gt=after).order_by('id')[:100]
    else:
        with_id = int(request.GET.get('with_id', 0) or 0)
        direct = (Message.objects.filter(id__gt=after, sender_id=my_id, sender_role=my_role, receiver_id=with_id, receiver_role=with_role) |
                  Message.objects.filter(id__gt=after, sender_id=with_id, sender_role=with_role, receiver_id=my_id, receiver_role=my_role))
        if my_role == 'agent' and with_role == 'admin':
            # Fold broadcast messages into the agent's thread with admin.
            broadcasts = Message.objects.filter(id__gt=after, is_broadcast=True, receiver_role='agent')
            msgs = (direct | broadcasts).order_by('id')[:100]
        else:
            msgs = direct.order_by('id')[:100]

    return JsonResponse({'messages': [_serialize(m) for m in msgs]})

@login_required
@require_POST
def api_send(request):
    _bump(request.user)
    try: data=json.loads(request.body)
    except: return JsonResponse({'error':'Invalid JSON'},status=400)
    content=(data.get('content') or '').strip()
    if not content: return JsonResponse({'error':'Missing fields'},status=400)
    my_id,my_role=_id(request.user)

    if data.get('broadcast'):
        if not request.user.is_staff:
            return JsonResponse({'error':'Only admin can broadcast'},status=403)
        m = Message.objects.create(sender_id=my_id, sender_role='admin', receiver_id=0,
                                    receiver_role='agent', content=content, is_broadcast=True)
    else:
        to_id=data.get('to_id'); to_role=data.get('to_role','agent')
        if to_id is None: return JsonResponse({'error':'Missing fields'},status=400)
        m=Message.objects.create(sender_id=my_id,sender_role=my_role,receiver_id=to_id,receiver_role=to_role,content=content)

    return JsonResponse({'message': _serialize(m)})

@login_required
def api_unread(request):
    my_id,my_role=_id(request.user)
    msgs=Message.objects.filter(receiver_id=my_id,receiver_role=my_role,read=False,is_broadcast=False)
    per={}
    for m in msgs:
        k=f'{m.sender_id}_{m.sender_role}'; per[k]=per.get(k,0)+1
    total = msgs.count()
    if my_role == 'agent':
        bcast_unread = Message.objects.filter(is_broadcast=True, read=False).count()
        if bcast_unread:
            per['0_admin'] = per.get('0_admin', 0) + bcast_unread
            total += bcast_unread
    return JsonResponse({'total':total,'per_contact':per})

@login_required
@require_POST
def api_mark_read(request):
    try: data=json.loads(request.body)
    except: return JsonResponse({'error':'bad json'},status=400)
    my_id,my_role=_id(request.user)
    from_id=data.get('from_id'); from_role=data.get('from_role')
    Message.objects.filter(sender_id=from_id,sender_role=from_role,receiver_id=my_id,receiver_role=my_role).update(read=True)
    if my_role == 'agent' and from_role == 'admin':
        Message.objects.filter(is_broadcast=True, read=False).update(read=True)
    return JsonResponse({'ok':True})
