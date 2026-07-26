from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from apps.requests_app.models import SupplyRequest
from apps.agents.models import Agent
from apps.messaging.models import Message

@login_required
def agent_supply_request(request):
    if request.user.is_staff: return redirect('admin_dashboard')
    if request.method=='POST':
        agent=get_object_or_404(Agent,user=request.user)
        SupplyRequest.objects.create(agent=agent,product_name=request.POST.get('product_name','').strip(),
            quantity=request.POST.get('quantity','').strip(),notes=request.POST.get('notes','').strip())
        messages.success(request,'Supply request submitted!')
    return redirect('agent_dashboard')

@staff_member_required
def admin_supply_requests(request):
    reqs=SupplyRequest.objects.select_related('agent__user').order_by('-created_at')
    return render(request,'admin/supply_requests.html',{'requests':reqs})

@staff_member_required
def admin_respond_supply(request,rid):
    if request.method=='POST':
        sr=get_object_or_404(SupplyRequest,pk=rid)
        sr.status=request.POST.get('status','approved'); sr.admin_response=request.POST.get('response','').strip(); sr.save()
        Message.objects.create(sender_id=request.user.id,sender_role='admin',receiver_id=sr.agent.id,receiver_role='agent',
            content=f"Your request for '{sr.product_name}' has been {sr.status}. {sr.admin_response}")
        messages.success(request,f'Request {sr.status}.')
    return redirect('admin_supply_requests')
