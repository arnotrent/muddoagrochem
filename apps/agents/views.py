import io
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import FileResponse, JsonResponse
from apps.agents.models import Agent
from apps.products.models import Product
from apps.requests_app.models import SupplyRequest
from apps.messaging.models import Message

def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff else 'agent_dashboard')
    if request.method=='POST':
        u=authenticate(request,username=request.POST.get('username','').strip(),password=request.POST.get('password',''))
        role=request.POST.get('role','agent')
        if u:
            if role=='admin' and u.is_staff: login(request,u); return redirect('admin_dashboard')
            elif role=='agent' and not u.is_staff:
                try:
                    a=u.agent_profile
                    if a.status!='active': messages.error(request,'Account deactivated.'); return render(request,'auth/login.html')
                    a.last_seen=timezone.now(); a.save(update_fields=['last_seen'])
                except Agent.DoesNotExist: pass
                login(request,u); return redirect('agent_dashboard')
            else: messages.error(request,'Wrong role selected.')
        else: messages.error(request,'Invalid username or password.')
    return render(request,'auth/login.html')

def logout_view(request): logout(request); return redirect('login')

@login_required
def agent_dashboard(request):
    if request.user.is_staff: return redirect('admin_dashboard')
    try: agent=request.user.agent_profile
    except: messages.error(request,'Agent profile not found.'); return redirect('login')
    agent.last_seen=timezone.now(); agent.save(update_fields=['last_seen'])
    my_requests=SupplyRequest.objects.filter(agent=agent).order_by('-created_at')[:10]
    unread=Message.objects.filter(receiver_id=agent.id,receiver_role='agent',read=False,is_broadcast=False).count()
    unread += Message.objects.filter(is_broadcast=True,read=False).exclude(sender_id=agent.id,sender_role='agent').count()
    last_msg=Message.objects.filter(sender_role='admin',receiver_id=agent.id,receiver_role='agent').order_by('-id').first()
    pending_count = sum(1 for r in my_requests if r.status == 'pending')
    kpis = [
        ('truck','my_requests', my_requests.count(), 'My Requests'),
        ('clock','pending', pending_count, 'Pending'),
        ('comment','unread', unread, 'Unread Messages'),
        ('flask','catalog', Product.objects.count(), 'Products in Catalogue'),
    ]
    return render(request,'agent/dashboard.html',{'agent':agent,'my_requests':my_requests,'unread':unread,'last_msg':last_msg,'total_products':Product.objects.count(),'kpis':kpis})

def _thread_summary(me_id, me_role, other_id, other_role):
    """Last direct message + unread count between `me` and one other party."""
    last = (Message.objects.filter(is_broadcast=False, sender_id=me_id, sender_role=me_role, receiver_id=other_id, receiver_role=other_role) |
            Message.objects.filter(is_broadcast=False, sender_id=other_id, sender_role=other_role, receiver_id=me_id, receiver_role=me_role)
            ).order_by('-id').first()
    unread = Message.objects.filter(is_broadcast=False, sender_id=other_id, sender_role=other_role,
                                     receiver_id=me_id, receiver_role=me_role, read=False).count()
    return last, unread

def _preview_for(msg):
    if not msg: return ''
    if msg.content: return msg.content[:44] + ('…' if len(msg.content) > 44 else '')
    return '📎 Attachment' if msg.attachment else ''

@login_required
def agent_chat(request):
    if request.user.is_staff: return redirect('admin_chat')
    agent=get_object_or_404(Agent,user=request.user)
    admin_u=User.objects.filter(is_staff=True).first()

    admin_last, admin_unread = (None, 0)
    if admin_u:
        admin_last, admin_unread = _thread_summary(agent.id, 'agent', admin_u.id, 'admin')

    other_agents = list(Agent.objects.filter(status='active').exclude(pk=agent.pk).select_related('user'))
    for a in other_agents:
        a.last_msg, a.unread_from = _thread_summary(agent.id, 'agent', a.id, 'agent')
        a.last_message_time = a.last_msg.created_at if a.last_msg else None
        a.last_message_preview = _preview_for(a.last_msg)
        a.last_message_mine = bool(a.last_msg and a.last_msg.sender_id == agent.id and a.last_msg.sender_role == 'agent')
    other_agents.sort(key=lambda a: (a.unread_from == 0, -(a.last_message_time.timestamp() if a.last_message_time else 0)))

    last_team = Message.objects.filter(is_broadcast=True).order_by('-id').first()

    return render(request,'agent/chat.html',{
        'agent': agent,
        'admin_id': admin_u.id if admin_u else 1,
        'admin_last_preview': _preview_for(admin_last),
        'admin_last_time': admin_last.created_at if admin_last else None,
        'admin_last_mine': bool(admin_last and admin_last.sender_role == 'agent'),
        'admin_unread': admin_unread,
        'other_agents': other_agents,
        'last_team': last_team,
        'last_team_preview': _preview_for(last_team),
    })

@login_required
def agent_profile(request):
    if request.user.is_staff: return redirect('admin_profile')
    agent = get_object_or_404(Agent, user=request.user)
    if request.method == 'POST':
        agent.display_name = request.POST.get('display_name','').strip()
        if 'avatar' in request.FILES:
            f = request.FILES['avatar']
            if f.name.rsplit('.',1)[-1].lower() in ('png','jpg','jpeg','gif','webp'):
                agent.avatar = f
        agent.save()
        messages.success(request, 'Profile updated!')
        return redirect('agent_profile')
    return render(request,'agent/profile.html',{'agent':agent})

@staff_member_required
def admin_agents(request):
    return render(request,'admin/agents.html',{'agents':Agent.objects.select_related('user').order_by('-created_at')})

@staff_member_required
def admin_add_agent(request):
    if request.method!='POST': return redirect('admin_agents')
    username=request.POST.get('username','').strip(); name=request.POST.get('name','').strip()
    if User.objects.filter(username=username).exists(): messages.error(request,'Username taken.'); return redirect('admin_agents')
    first,*rest=name.split(' ',1)
    u=User.objects.create_user(username=username,email=request.POST.get('email','').strip(),password=request.POST.get('password',''),first_name=first,last_name=' '.join(rest) if rest else '')
    Agent.objects.create(user=u,phone=request.POST.get('phone','').strip(),region=request.POST.get('region','').strip(),district=request.POST.get('district','').strip())
    messages.success(request,f'Agent {name} added!'); return redirect('admin_agents')

@staff_member_required
def admin_delete_agent(request,aid):
    if request.method=='POST': get_object_or_404(Agent,pk=aid).user.delete(); messages.success(request,'Agent removed.')
    return redirect('admin_agents')

@staff_member_required
def admin_toggle_agent(request,aid):
    if request.method=='POST':
        a=get_object_or_404(Agent,pk=aid); a.status='inactive' if a.status=='active' else 'active'; a.save(update_fields=['status'])
        messages.success(request,f'Agent set to {a.status}.')
    return redirect('admin_agents')

def api_agents_status(request):
    """Live online/offline status for chat presence dots + the active-agents counter."""
    if not request.user.is_authenticated:
        return JsonResponse({'online': {}})
    return JsonResponse({'online': {str(a.id): a.is_online for a in Agent.objects.all()}})

@staff_member_required
def agent_report_pdf(request,aid):
    from reportlab.lib.pagesizes import A4; from reportlab.lib.units import mm; from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle; from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer
    from reportlab.lib.enums import TA_RIGHT; from datetime import datetime
    agent=get_object_or_404(Agent,pk=aid); reqs=SupplyRequest.objects.filter(agent=agent).order_by('-created_at')
    buf=io.BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,topMargin=18*mm,bottomMargin=18*mm)
    DARK=colors.HexColor('#1e293b'); MID=colors.HexColor('#38bdf8'); WHT=colors.white; LGRY=colors.HexColor('#f5f5f5'); LGRN=colors.HexColor('#eef2f6'); GOLD=colors.HexColor('#0ea5e9'); MUTED=colors.HexColor('#565656')
    h1=ParagraphStyle('h1',fontName='Helvetica-Bold',fontSize=20,textColor=WHT); h2=ParagraphStyle('h2',fontName='Helvetica-Bold',fontSize=12,textColor=DARK)
    bd=ParagraphStyle('bd',fontName='Helvetica-Bold',fontSize=10,textColor=colors.HexColor('#111')); sm=ParagraphStyle('sm',fontName='Helvetica',fontSize=8.5,textColor=MUTED); lb=ParagraphStyle('lb',fontName='Helvetica-Bold',fontSize=9.5,textColor=MUTED)
    story=[]
    hdr=Table([[Paragraph('<b>AGENT REPORT</b>',h1),Paragraph(f'<b>{agent.name}</b><br/><font size="10">{agent.region or "—"} Region</font>',ParagraphStyle('r',fontName='Helvetica-Bold',fontSize=14,textColor=GOLD,alignment=TA_RIGHT))]],colWidths=[100*mm,74*mm])
    hdr.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),DARK),('PADDING',(0,0),(-1,-1),14),('VALIGN',(0,0),(-1,-1),'MIDDLE')])); story.append(hdr)
    band=Table([[Paragraph(f'MUDDO AGRO CHEMICALS LTD · Report: {datetime.now().strftime("%d %B %Y")}',sm)]],colWidths=[174*mm])
    band.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LGRN),('PADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),1.5,MID)])); story+=[band,Spacer(1,8*mm)]
    prof=[('Full Name',agent.name),('Username',agent.username),('Email',agent.email or '—'),('Phone',agent.phone or '—'),('Region',agent.region or '—'),('District',agent.district or '—'),('Status',agent.status.title()),('Joined',agent.created_at.strftime('%Y-%m-%d') if agent.created_at else '—'),('Last Active',agent.last_seen.strftime('%Y-%m-%d %H:%M') if agent.last_seen else 'Never')]
    pr=[[Paragraph(k,lb),Paragraph(v,bd)] for k,v in prof]; pt=Table(pr,colWidths=[55*mm,119*mm])
    pt.setStyle(TableStyle([('ROWBACKGROUNDS',(0,0),(-1,-1),[WHT,LGRY]),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),10),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#e0e0e0')),('LINEBELOW',(0,-1),(-1,-1),1.5,MID)]))
    story+=[Paragraph('<b>AGENT PROFILE</b>',h2),Spacer(1,3*mm),pt,Spacer(1,8*mm)]
    if reqs.exists():
        sr=[[Paragraph(h,ParagraphStyle('th',fontName='Helvetica-Bold',fontSize=9,textColor=WHT)) for h in ['#','Product','Qty','Status','Date']]]
        for i,r in enumerate(reqs): sr.append([str(i+1),r.product_name,r.quantity,r.status.title(),r.created_at.strftime('%Y-%m-%d')])
        srt=Table(sr,colWidths=[10*mm,75*mm,35*mm,30*mm,24*mm])
        srt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),DARK),('TEXTCOLOR',(0,0),(-1,0),WHT),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('ROWBACKGROUNDS',(0,1),(-1,-1),[WHT,LGRY]),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),8),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#e0e0e0'))]))
        story+=[Paragraph('<b>SUPPLY REQUEST HISTORY</b>',h2),Spacer(1,3*mm),srt]
    doc.build(story); buf.seek(0)
    return FileResponse(buf,as_attachment=True,filename=f'MACL_Agent_{agent.name.replace(" ","_")}.pdf',content_type='application/pdf')
