import io,csv,json,random,string
from datetime import datetime,timedelta
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse,FileResponse
from django.db.models import Count,F
from django.utils import timezone
from apps.products.models import Product
from apps.inventory.models import Inventory,InventoryLog
from apps.core.models import ContactRequest,NewsletterSubscriber,StaffProfile,SiteSettings,FAQ
from apps.agents.models import Agent
from apps.requests_app.models import SupplyRequest
from apps.messaging.models import Message
from apps.distributors.models import Distributor

@staff_member_required
def admin_dashboard(request):
    stats={'total_products':Product.objects.count(),'total_distributors':Distributor.objects.count(),
           'new_requests':ContactRequest.objects.filter(status='new').count(),
           'total_requests':ContactRequest.objects.count(),'total_agents':Agent.objects.count(),
           'active_agents':Agent.objects.filter(status='active').count(),
           'pending_supply':SupplyRequest.objects.filter(status='pending').count(),
           'unread_msgs':Message.objects.filter(receiver_role='admin',read=False).count(),
           'low_stock':Inventory.objects.filter(stock_qty__lte=F('reorder_level')).count()}
    return render(request,'admin/dashboard.html',{
        'stats':stats,'recent_requests':ContactRequest.objects.order_by('-created_at')[:5],
        'agents':Agent.objects.select_related('user').order_by('-last_seen')[:10],
        'recent_supply':SupplyRequest.objects.select_related('agent__user').order_by('-created_at')[:5],
        'low_stock_items':Inventory.objects.filter(stock_qty__lte=F('reorder_level')).select_related('product').order_by('stock_qty')[:5]})

@staff_member_required
def admin_products(request):
    return render(request,'admin/products.html',{'products':Product.objects.select_related('inventory').order_by('category','name')})

@staff_member_required
def admin_add_product(request):
    if request.method!='POST': return redirect('admin_products')
    name = request.POST.get('name','').strip()
    existing = Product.objects.filter(name__iexact=name).first()
    if existing:
        messages.error(request, f'"{name}" already exists in the catalogue — edit that product instead of adding a duplicate.')
        return redirect('admin_products')
    img=None
    if 'product_image' in request.FILES:
        f=request.FILES['product_image']
        if f.name.rsplit('.',1)[-1].lower() in ['png','jpg','jpeg','gif','webp']: img=f
    p=Product.objects.create(name=name,category=request.POST.get('category','other'),
        description=request.POST.get('description','').strip(),active_ingredient=request.POST.get('active_ingredient','').strip(),
        formulation=request.POST.get('formulation','').strip(),crops=request.POST.get('crops','').strip(),
        dosage=request.POST.get('dosage','').strip(),packing=request.POST.get('packing','').strip(),
        image_url=request.POST.get('image_url','').strip(),image_file=img)
    Inventory.objects.create(product=p,stock_qty=int(request.POST.get('stock_qty',0) or 0),
        reorder_level=int(request.POST.get('reorder_level',10) or 10),unit=request.POST.get('unit','units'))
    messages.success(request,f'Product "{p.name}" added!'); return redirect('admin_products')

@staff_member_required
def admin_edit_product(request, pid):
    p = get_object_or_404(Product, pk=pid)
    if request.method != 'POST':
        return redirect('admin_products')
    p.name              = request.POST.get('name', p.name).strip()
    p.category          = request.POST.get('category', p.category)
    p.description       = request.POST.get('description', '').strip()
    p.active_ingredient = request.POST.get('active_ingredient', '').strip()
    p.formulation       = request.POST.get('formulation', '').strip()
    p.crops             = request.POST.get('crops', '').strip()
    p.dosage            = request.POST.get('dosage', '').strip()
    p.packing           = request.POST.get('packing', '').strip()
    if request.POST.get('image_url', '').strip():
        p.image_url = request.POST.get('image_url').strip()
    if 'product_image' in request.FILES:
        f = request.FILES['product_image']
        if f.name.rsplit('.', 1)[-1].lower() in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
            p.image_file = f
    p.save()
    inv, _ = Inventory.objects.get_or_create(product=p, defaults={'stock_qty': 0})
    inv.stock_qty = int(request.POST.get('stock_qty', inv.stock_qty) or 0)
    inv.reorder_level = int(request.POST.get('reorder_level', inv.reorder_level) or 10)
    inv.save()
    messages.success(request, f'"{p.name}" updated!')
    return redirect('admin_products')

@staff_member_required
def admin_delete_product(request,pid):
    if request.method=='POST':
        p=get_object_or_404(Product,pk=pid); name=p.name; p.delete(); messages.success(request,f'"{name}" deleted.')
    return redirect('admin_products')

@staff_member_required
def admin_requests(request):
    return render(request,'admin/requests.html',{'requests':ContactRequest.objects.order_by('-created_at')})

@staff_member_required
def admin_update_request(request,rid):
    if request.method=='POST':
        cr=get_object_or_404(ContactRequest,pk=rid); cr.status=request.POST.get('status','resolved'); cr.save(update_fields=['status'])
    return redirect('admin_requests')

# ─────────────────────────────────────────────────────────────────
# DISTRIBUTOR LOCATION SAFEGUARDS — rough bounding boxes, catches
# gross data-entry mistakes (a pin in the ocean, wrong continent, etc).
# ─────────────────────────────────────────────────────────────────
COUNTRY_BOUNDS = {
    'Uganda':      (-1.50,  4.30, 29.50, 35.10),
    'Kenya':       (-4.90,  5.20, 33.90, 41.90),
    'Tanzania':    (-11.80, -0.90, 29.30, 40.50),
    'Rwanda':      (-2.95, -1.00, 28.80, 30.95),
    'Burundi':     (-4.50, -2.30, 28.90, 30.90),
    'South Sudan': (3.40,  12.30, 24.10, 35.95),
    'DR Congo':    (-13.50, 5.40, 12.15, 31.30),
}

def _within_country(country, lat, lng):
    b = COUNTRY_BOUNDS.get(country)
    if not b:
        return True
    min_lat, max_lat, min_lng, max_lng = b
    return min_lat <= lat <= max_lat and min_lng <= lng <= max_lng

@staff_member_required
def admin_distributors(request):
    return render(request,'admin/distributors.html',{
        'distributors':Distributor.objects.order_by('country','region','name'),
        'countries': Distributor.COUNTRIES,
    })

@staff_member_required
def admin_add_distributor(request):
    if request.method=='POST':
        country = (request.POST.get('country','Uganda') or 'Uganda').strip()
        try:
            lat=float(request.POST.get('lat',0) or 0); lng=float(request.POST.get('lng',0) or 0)
        except ValueError:
            lat=lng=0.0
        if (lat, lng) == (0.0, 0.0):
            messages.error(request, 'Please pick the outlet\u2019s exact spot on the map before saving \u2014 the location was left blank.')
            return redirect('admin_distributors')
        if not _within_country(country, lat, lng):
            messages.error(request, f'That map pin doesn\u2019t fall inside {country} \u2014 it looks like it\u2019s over water, or in another country. Please reposition it and try again.')
            return redirect('admin_distributors')
        Distributor.objects.create(name=request.POST.get('name','').strip(),country=country,
            region=request.POST.get('region','').strip(),
            district=request.POST.get('district','').strip(),address=request.POST.get('address','').strip(),
            phone=request.POST.get('phone','').strip(),email=request.POST.get('email','').strip(),
            lat=lat,lng=lng)
        messages.success(request,'Distributor added!')
    return redirect('admin_distributors')

@staff_member_required
def admin_edit_distributor(request, did):
    d = get_object_or_404(Distributor, pk=did)
    if request.method == 'POST':
        country = (request.POST.get('country', d.country) or d.country).strip()
        try:
            lat=float(request.POST.get('lat', d.lat) or d.lat); lng=float(request.POST.get('lng', d.lng) or d.lng)
        except ValueError:
            lat, lng = d.lat, d.lng
        if not _within_country(country, lat, lng):
            messages.error(request, f'That map pin doesn\u2019t fall inside {country} \u2014 it looks like it\u2019s over water, or in another country. Please reposition it and try again.')
            return redirect('admin_distributors')
        d.name     = request.POST.get('name', d.name).strip()
        d.country  = country
        d.region   = request.POST.get('region', d.region).strip()
        d.district = request.POST.get('district', d.district).strip()
        d.address  = request.POST.get('address', '').strip()
        d.phone    = request.POST.get('phone', '').strip()
        d.email    = request.POST.get('email', '').strip()
        d.lat, d.lng = lat, lng
        d.save()
        messages.success(request, f'"{d.name}" updated!')
    return redirect('admin_distributors')

@staff_member_required
def admin_delete_distributor(request,did):
    if request.method=='POST': get_object_or_404(Distributor,pk=did).delete(); messages.success(request,'Distributor removed.')
    return redirect('admin_distributors')

@staff_member_required
def admin_inventory(request):
    return render(request,'admin/inventory.html',{
        'items':Inventory.objects.select_related('product').order_by('product__category','product__name'),
        'log':InventoryLog.objects.select_related('product').order_by('-created_at')[:40]})

@staff_member_required
def admin_update_inventory(request):
    if request.method!='POST': return JsonResponse({'error':'POST required'},status=405)
    pid=int(request.POST.get('product_id',0)); action=request.POST.get('action','set')
    qty=int(request.POST.get('qty',0) or 0); reason=request.POST.get('reason','Manual update')
    inv,_=Inventory.objects.get_or_create(product_id=pid,defaults={'stock_qty':0})
    cur=inv.stock_qty
    new_qty=cur+qty if action=='add' else (max(0,cur-qty) if action=='remove' else qty)
    change=new_qty-cur; inv.stock_qty=new_qty; inv.reorder_level=int(request.POST.get('reorder_level',10) or 10); inv.save()
    InventoryLog.objects.create(product_id=pid,change_qty=change,reason=reason,changed_by=request.user.username)
    return JsonResponse({'ok':True,'new_qty':new_qty})

@staff_member_required
def admin_newsletter(request):
    subs=NewsletterSubscriber.objects.order_by('-subscribed_at')
    return render(request,'admin/newsletter.html',{'subscribers':subs,'active_count':subs.filter(active=True).count()})

@staff_member_required
def admin_import(request):
    results=None
    if request.method=='POST':
        f=request.FILES.get('csv_file')
        if not f or not f.name.endswith('.csv'): messages.error(request,'Upload a .csv file.'); return redirect('admin_import')
        reader=csv.DictReader(io.StringIO(f.read().decode('utf-8-sig',errors='replace')))
        added=0; skipped=0; errors=[]
        for row in reader:
            try:
                name=(row.get('name') or '').strip(); cat=(row.get('category') or '').strip().lower()
                if not name or cat not in ('pesticide','herbicide','fungicide','other'): skipped+=1; continue
                p,created=Product.objects.get_or_create(name=name,defaults={'category':cat,'description':(row.get('description') or '').strip(),'active_ingredient':(row.get('active_ingredient') or '').strip(),'formulation':(row.get('formulation') or '').strip(),'crops':(row.get('crops') or '').strip(),'dosage':(row.get('dosage') or '').strip(),'packing':(row.get('packing') or '').strip(),'image_url':(row.get('image_url') or '').strip()})
                if created: Inventory.objects.get_or_create(product=p,defaults={'stock_qty':0}); added+=1
                else: skipped+=1
            except Exception as e: errors.append(str(e))
        results={'added':added,'skipped':skipped,'errors':errors}
    return render(request,'admin/import.html',{'results':results})

@staff_member_required
def admin_settings(request):
    if request.method=='POST':
        action=request.POST.get('action')
        if action=='change_password':
            old=request.POST.get('old_password',''); new=request.POST.get('new_password',''); conf=request.POST.get('confirm_password','')
            if new!=conf: messages.error(request,'Passwords do not match.')
            elif len(new)<8: messages.error(request,'Password must be at least 8 characters.')
            elif not request.user.check_password(old): messages.error(request,'Current password incorrect.')
            else: request.user.set_password(new); request.user.save(); messages.success(request,'Password updated. Please log in again.'); return redirect('login')
        elif action=='reset_agent_password':
            aid=int(request.POST.get('agent_id',0)); pw=request.POST.get('new_agent_password','')
            if len(pw)<6: messages.error(request,'Password must be at least 6 characters.')
            else:
                a=get_object_or_404(Agent,pk=aid); a.user.set_password(pw); a.user.save(); messages.success(request,f'Password reset for {a.name}.')
    agents=Agent.objects.select_related('user').order_by('user__first_name')
    sysinfo=[('Total Products',str(Product.objects.count())),('Total Agents',str(Agent.objects.count())),('Total Enquiries',str(ContactRequest.objects.count())),('Distributors',str(Distributor.objects.count())),('Logged in as',request.user.username),('Django',__import__('django').get_version())]
    return render(request,'admin/settings.html',{'agents':agents,'sysinfo':sysinfo})

@staff_member_required
def admin_profile(request):
    profile, _ = StaffProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.display_name = request.POST.get('display_name','').strip()
        if 'avatar' in request.FILES:
            f = request.FILES['avatar']
            if f.name.rsplit('.',1)[-1].lower() in ('png','jpg','jpeg','gif','webp'):
                profile.avatar = f
        profile.save()
        messages.success(request, 'Profile updated!')
        return redirect('admin_profile')
    return render(request,'admin/profile.html',{'profile':profile})

# ─────────────────────────────────────────────────────────────────
# SITE CONTENT — company info + FAQ, editable by admin instead of
# hardcoded. Both feed apps/core/views.py (About/Contact pages).
# ─────────────────────────────────────────────────────────────────
@staff_member_required
def admin_site_content(request):
    site = SiteSettings.load()
    faqs = FAQ.objects.all()
    return render(request,'admin/site_content.html',{'site':site,'faqs':faqs})

@staff_member_required
def admin_update_site_settings(request):
    if request.method == 'POST':
        site = SiteSettings.load()
        site.year_founded            = request.POST.get('year_founded', site.year_founded).strip()
        site.company_phone           = request.POST.get('company_phone', site.company_phone).strip()
        site.company_phone_secondary = request.POST.get('company_phone_secondary', '').strip()
        site.company_email           = request.POST.get('company_email', site.company_email).strip()
        site.company_address         = request.POST.get('company_address', site.company_address).strip()
        site.business_hours          = request.POST.get('business_hours', site.business_hours).strip()
        site.whatsapp_number         = request.POST.get('whatsapp_number', site.whatsapp_number).strip()
        site.facebook_url            = request.POST.get('facebook_url', '').strip()
        site.save()
        messages.success(request, 'Site details updated — About, Contact and the footer now reflect this.')
    return redirect('admin_site_content')

@staff_member_required
def admin_add_faq(request):
    if request.method == 'POST':
        q = request.POST.get('question','').strip(); a = request.POST.get('answer','').strip()
        if q and a:
            max_order = FAQ.objects.count()
            FAQ.objects.create(question=q, answer=a, order=max_order, active=True)
            messages.success(request, 'FAQ added!')
        else:
            messages.error(request, 'Both a question and an answer are required.')
    return redirect('admin_site_content')

@staff_member_required
def admin_edit_faq(request, fid):
    faq = get_object_or_404(FAQ, pk=fid)
    if request.method == 'POST':
        faq.question = request.POST.get('question', faq.question).strip()
        faq.answer   = request.POST.get('answer', faq.answer).strip()
        faq.active   = request.POST.get('active') == 'on'
        faq.save()
        messages.success(request, 'FAQ updated!')
    return redirect('admin_site_content')

@staff_member_required
def admin_delete_faq(request, fid):
    if request.method == 'POST':
        get_object_or_404(FAQ, pk=fid).delete()
        messages.success(request, 'FAQ removed.')
    return redirect('admin_site_content')

@staff_member_required
def api_analytics(request):
    from django.db.models.functions import TruncDate
    since=timezone.now()-timedelta(days=14)
    daily=(ContactRequest.objects.filter(created_at__gte=since).annotate(day=TruncDate('created_at')).values('day').annotate(cnt=Count('id')).order_by('day'))
    return JsonResponse({'daily_enquiries':[{'day':str(r['day']),'cnt':r['cnt']} for r in daily],'supply_by_status':list(SupplyRequest.objects.values('status').annotate(cnt=Count('id'))),'products_by_cat':list(Product.objects.values('category').annotate(cnt=Count('id')))})
