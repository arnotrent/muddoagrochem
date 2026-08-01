import json
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
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
        preview = ''
        if m:
            preview = (m.content[:46] + ('…' if len(m.content) > 46 else '')) if m.content else ('📎 Attachment' if m.attachment else '')
        a.last_message_preview = preview
        a.last_message_time = m.created_at if m else None
        a.last_message_mine = bool(m and m.sender_role == 'admin')
        a.unread_from = unread_map.get(str(a.id), 0)

    agents.sort(key=lambda a: (a.unread_from == 0, -(a.last_message_time.timestamp() if a.last_message_time else 0)))

    last_team = Message.objects.filter(is_broadcast=True).order_by('-id').first()
    last_team_preview = ''
    if last_team:
        last_team_preview = (last_team.content[:38] + ('…' if len(last_team.content) > 38 else '')) if last_team.content else '📎 Attachment'

    return render(request, 'admin/chat.html', {
        'agents': agents,
        'unread_map': unread_map,
        'last_team': last_team,
        'last_team_preview': last_team_preview,
    })

def _id(user):
    if user.is_staff: return user.id,'admin'
    try: return user.agent_profile.id,'agent'
    except: return user.id,'agent'

def _bump(user):
    if not user.is_staff:
        try: user.agent_profile.last_seen=timezone.now(); user.agent_profile.save(update_fields=['last_seen'])
        except: pass

def _display_name(role, sid):
    if role == 'admin':
        u = User.objects.filter(pk=sid, is_staff=True).first()
        if u:
            try: return u.staff_profile.name
            except Exception: return u.get_full_name() or u.username
        return 'Admin'
    a = Agent.objects.filter(pk=sid).first()
    return a.name if a else 'Agent'

def _avatar_url(role, sid):
    if role == 'admin':
        u = User.objects.filter(pk=sid).first()
        if u:
            try: return u.staff_profile.avatar_url
            except Exception: return None
        return None
    a = Agent.objects.filter(pk=sid).first()
    return a.avatar_url if a else None

def _serialize(m):
    reply = None
    if m.reply_to_id:
        r = m.reply_to
        if r:
            reply = {
                'id': r.id,
                'sender_role': r.sender_role,
                'sender_name': _display_name(r.sender_role, r.sender_id),
                'content': r.content[:80] if r.content else ('📎 Attachment' if r.attachment else ''),
            }
    return {
        'id': m.id, 'sender_id': m.sender_id, 'sender_role': m.sender_role,
        'sender_name': _display_name(m.sender_role, m.sender_id),
        'sender_avatar_url': _avatar_url(m.sender_role, m.sender_id),
        'receiver_id': m.receiver_id, 'receiver_role': m.receiver_role,
        'content': m.content, 'read': m.read, 'is_broadcast': m.is_broadcast,
        'reply_to': reply,
        'attachment_url': m.attachment.url if m.attachment else None,
        'attachment_name': m.attachment.name.rsplit('/', 1)[-1] if m.attachment else None,
        'attachment_is_image': m.attachment_is_image,
        'created_at': m.created_at.isoformat(),
    }

@login_required
def api_messages(request):
    _bump(request.user)
    with_role = request.GET.get('with_role', 'agent')
    after = int(request.GET.get('after', 0) or 0)
    my_id, my_role = _id(request.user)

    if with_role == 'broadcast':
        # The shared Team channel — visible to admin and every agent alike.
        msgs = Message.objects.filter(is_broadcast=True, id__gt=after).order_by('id')[:150]
    else:
        with_id = int(request.GET.get('with_id', 0) or 0)
        msgs = (Message.objects.filter(id__gt=after, sender_id=my_id, sender_role=my_role, receiver_id=with_id, receiver_role=with_role, is_broadcast=False) |
                Message.objects.filter(id__gt=after, sender_id=with_id, sender_role=with_role, receiver_id=my_id, receiver_role=my_role, is_broadcast=False)
                ).order_by('id')[:100]

    return JsonResponse({'messages': [_serialize(m) for m in msgs]})

@login_required
@require_POST
def api_send(request):
    _bump(request.user)
    my_id, my_role = _id(request.user)

    is_multipart = bool(request.content_type) and request.content_type.startswith('multipart')
    attachment = None
    if is_multipart:
        data = request.POST
        attachment = request.FILES.get('attachment')
    else:
        try: data = json.loads(request.body)
        except: return JsonResponse({'error': 'Invalid JSON'}, status=400)

    content = (data.get('content') or '').strip()
    if not content and not attachment:
        return JsonResponse({'error': 'A message needs text or an attachment'}, status=400)

    reply_to = None
    reply_to_id = data.get('reply_to')
    if reply_to_id:
        reply_to = Message.objects.filter(pk=reply_to_id).first()

    is_broadcast = str(data.get('broadcast', '')).lower() in ('true', '1', 'on')

    if is_broadcast:
        # Team channel — open to admin AND every agent, not admin-only.
        m = Message.objects.create(sender_id=my_id, sender_role=my_role, receiver_id=0,
                                    receiver_role='agent', content=content, is_broadcast=True,
                                    reply_to=reply_to, attachment=attachment)
    else:
        to_id = data.get('to_id'); to_role = data.get('to_role', 'agent')
        if to_id is None: return JsonResponse({'error': 'Missing fields'}, status=400)
        m = Message.objects.create(sender_id=my_id, sender_role=my_role, receiver_id=to_id,
                                    receiver_role=to_role, content=content, reply_to=reply_to,
                                    attachment=attachment)

    return JsonResponse({'message': _serialize(m)})

@login_required
def api_unread(request):
    my_id,my_role=_id(request.user)
    msgs=Message.objects.filter(receiver_id=my_id,receiver_role=my_role,read=False,is_broadcast=False)
    per={}
    for m in msgs:
        k=f'{m.sender_id}_{m.sender_role}'; per[k]=per.get(k,0)+1
    total = msgs.count()
    # Team-channel unread: anything not sent by me and not yet read.
    bcast_unread = Message.objects.filter(is_broadcast=True, read=False).exclude(sender_id=my_id, sender_role=my_role).count()
    if bcast_unread:
        per['0_broadcast'] = bcast_unread
        total += bcast_unread
    return JsonResponse({'total':total,'per_contact':per})

@login_required
@require_POST
def api_mark_read(request):
    try: data=json.loads(request.body)
    except: return JsonResponse({'error':'bad json'},status=400)
    my_id,my_role=_id(request.user)
    from_id=data.get('from_id'); from_role=data.get('from_role')
    if from_role == 'broadcast':
        Message.objects.filter(is_broadcast=True, read=False).exclude(sender_id=my_id, sender_role=my_role).update(read=True)
    else:
        Message.objects.filter(sender_id=from_id,sender_role=from_role,receiver_id=my_id,receiver_role=my_role,is_broadcast=False).update(read=True)
    return JsonResponse({'ok':True})
