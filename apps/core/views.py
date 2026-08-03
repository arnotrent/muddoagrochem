import json, random, string
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from apps.core.models import ContactRequest, NewsletterSubscriber, SiteSettings, FAQ
from apps.products.models import Product
from apps.distributors.models import Distributor

def _send(subj, to, body):
    try: send_mail(subj, body, settings.DEFAULT_FROM_EMAIL, to, fail_silently=True)
    except: pass

def _ref(): return 'ENQ-'+''.join(random.choices(string.ascii_uppercase+string.digits,k=8))

def index(request):
    stats = {k: Product.objects.filter(category=v).count()
             for k,v in [('pesticides','pesticide'),('herbicides','herbicide'),('fungicides','fungicide'),('other','other')]}
    stats['distributors'] = Distributor.objects.count()
    all_p = list(Product.objects.all())
    featured = random.sample(all_p, min(6, len(all_p)))
    why_cards = [
        ('shield-alt','100% Authentic','All products MAAIF-registered, sourced directly from certified manufacturers. Zero counterfeits.'),
        ('users','Farmer First','Pricing and advice built around Uganda\'s farmers — retail and wholesale, no minimum order.'),
        ('flask','Quality Assured','Every product meets MAAIF registration and international quality standards before we stock it.'),
        ('map-marked-alt','Nationwide Reach','11 authorised outlets across Central, Eastern, Northern and Western Uganda.'),
        ('headset','Expert Support','Our trained team gives dosage guidance, application timing and crop-specific advice — free.'),
        ('handshake','Long-term Partners','We build lasting relationships with farmers and distributors, not just one-off transactions.'),
    ]
    categories = [
        ('bug','Pesticides','pesticides','/static/images/hero_pesticides.jpg'),
        ('seedling','Herbicides','herbicides','/static/images/hero_herbicides.jpg'),
        ('microscope','Fungicides','fungicides','/static/images/hero_fungicides.jpg'),
        ('boxes','Fertilizers & Equipment','other_products','/static/images/hero_fertilizers.jpg'),
    ]
    return render(request,'index.html',{'stats':stats,'featured':featured,'why_cards':why_cards,'categories':categories})

def about(request):
    site = SiteSettings.load()
    stats_list=[(site.year_founded,'Year Founded'),(f'{Product.objects.count()}+','Product Lines'),
                (f'{Distributor.objects.count()}+','Distributor Outlets'),('4','Regions Covered')]
    faqs = FAQ.objects.filter(active=True)
    categories_meta = [
        ('pesticide',  'bug',        'Pesticides',        'images/thumb_pesticides.jpg',
         "Fast, reliable knockdown for the insects that eat into your harvest — from aphids and bollworm to stem borers."),
        ('herbicide',  'seedling',   'Herbicides',        'images/thumb_herbicides.jpg',
         "Clear stubborn weeds like Couch and Kikuyu grass without setting your crop back — selective and non-selective options."),
        ('fungicide',  'microscope', 'Fungicides',        'images/thumb_fungicides.jpg',
         "Protective and curative cover against blight, mildew and rot — built for Uganda's humidity and rainfall patterns."),
        ('other',      'boxes',      'Fertilizers & Equipment', 'images/thumb_fertilizers.jpg',
         "Balanced nutrition and the spraying equipment to apply it right — from basal fertilizer to a dependable knapsack sprayer."),
    ]
    product_groups = []
    for cat, icon, title, thumb, blurb in categories_meta:
        products = Product.objects.filter(category=cat)
        if products.exists():
            product_groups.append({'icon': icon, 'title': title, 'thumb': thumb, 'blurb': blurb, 'products': products})
    return render(request,'about.html',{'stats_list':stats_list,'faqs':faqs,'product_groups':product_groups,'site':site})

def contact(request):
    site = SiteSettings.load()
    if request.method=='POST':
        ref=_ref()
        cr=ContactRequest.objects.create(
            ref_number=ref, name=request.POST.get('name','').strip(),
            email=request.POST.get('email','').strip(), phone=request.POST.get('phone','').strip(),
            subject=request.POST.get('subject','').strip(), message=request.POST.get('message','').strip())
        _send(f'Muddo Agro — Enquiry Received [{ref}]',[cr.email],
              f"Dear {cr.name},\n\nThank you for contacting Muddo Agro Chemicals LTD.\nYour reference: {ref}\n\nWe'll respond within 1 business day.\n\nMuddo Agro Team\n{site.company_phone}")
        _send(f'New Enquiry [{ref}] — {cr.subject}',[site.company_email],
              f"From: {cr.name} <{cr.email}>\nPhone: {cr.phone}\nSubject: {cr.subject}\n\n{cr.message}")
        messages.success(request,f'Message sent! Reference: <strong>{ref}</strong> — save it to track your enquiry.')
        return redirect('contact')
    phone_lines = site.company_phone
    if site.company_phone_secondary:
        phone_lines += f'<br>{site.company_phone_secondary}'
    phone_links = ' / '.join(f'<a href="tel:{p.strip()}">{p.strip()}</a>' for p in site.company_phone.split('/'))
    contact_items = [
        ('map-marker-alt','Visit us in Kampala', site.company_address, ''),
        ('phone','Call or WhatsApp us', phone_links + (f'<br><a href="tel:{site.company_phone_secondary.split("/")[0].strip()}">{site.company_phone_secondary}</a>' if site.company_phone_secondary else ''), ''),
        ('envelope','Email the team', f'<a href="mailto:{site.company_email}">{site.company_email}</a>', ''),
        ('clock','When we\'re open', site.business_hours, ''),
    ]
    if site.facebook_url:
        contact_items.append(('facebook','Follow along on Facebook', f'<a href="{site.facebook_url}" target="_blank">MUDDO AGRO Chemicals LTD</a>', ''))
    return render(request,'contact.html',{'contact_items':contact_items,'site':site})

def track(request):
    ref=request.GET.get('ref','').strip().upper(); result=None; rows=[]
    if ref:
        try:
            result=ContactRequest.objects.get(ref_number=ref)
            rows=[('Name',result.name),('Email',result.email),('Phone',result.phone or '—'),
                  ('Subject',result.subject),('Status',result.status.title()),
                  ('Date',result.created_at.strftime('%d %b %Y %H:%M')),('Message',result.message)]
        except ContactRequest.DoesNotExist: pass
    return render(request,'track.html',{'ref':ref,'result':result,'enquiry_rows':rows})

def search(request):
    q=request.GET.get('q','').strip(); results={'products':[],'distributors':[]}
    if q and len(q)>=2:
        results['products']=list((Product.objects.filter(name__icontains=q)|
            Product.objects.filter(active_ingredient__icontains=q)|
            Product.objects.filter(crops__icontains=q)|
            Product.objects.filter(description__icontains=q)).distinct()[:20])
        results['distributors']=list((Distributor.objects.filter(name__icontains=q)|
            Distributor.objects.filter(district__icontains=q)|
            Distributor.objects.filter(region__icontains=q)).distinct()[:10])
    return render(request,'search.html',{'q':q,'results':results})

def api_search(request):
    q=request.GET.get('q','').strip()
    if len(q)<2: return JsonResponse([],safe=False)
    products=(Product.objects.filter(name__icontains=q)|Product.objects.filter(active_ingredient__icontains=q))[:8]
    return JsonResponse([{'id':p.id,'name':p.name,'category':p.category,'image':p.display_image} for p in products],safe=False)

def compare(request):
    pl=[{'id':p.id,'name':p.name,'category':p.category,'description':p.description or '',
         'active_ingredient':p.active_ingredient or '','formulation':p.formulation or '',
         'crops':p.crops or '','dosage':p.dosage or '','packing':p.packing or '',
         'image_url':p.display_image,'stock_qty':p.stock_qty} for p in Product.objects.all()]
    return render(request,'compare.html',{'all_products':pl,'all_products_json':json.dumps(pl)})

def subscribe(request):
    if request.method!='POST': return JsonResponse({'ok':False},status=405)
    try: data=json.loads(request.body)
    except: data={}
    email=(data.get('email') or '').strip().lower()
    if not email or '@' not in email: return JsonResponse({'ok':False,'message':'Invalid email.'},status=400)
    obj,created=NewsletterSubscriber.objects.get_or_create(email=email,defaults={'name':data.get('name',''),'active':True})
    if not created and obj.active: return JsonResponse({'ok':True,'message':"Already subscribed!"})
    if not created: obj.active=True; obj.save()
    return JsonResponse({'ok':True,'message':"Subscribed! You'll receive our latest updates."})

def sitemap(request):
    base=request.build_absolute_uri('/').rstrip('/')
    urls=[('/',1.0,'weekly'),('/pesticides/',0.9,'weekly'),('/herbicides/',0.9,'weekly'),
          ('/fungicides/',0.9,'weekly'),('/other-products/',0.9,'weekly'),
          ('/distributors/',0.8,'monthly'),('/contact/',0.7,'monthly'),('/about/',0.6,'monthly')]
    xml=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path,pri,freq in urls: xml.append(f'  <url><loc>{base}{path}</loc><priority>{pri}</priority><changefreq>{freq}</changefreq></url>')
    for p in Product.objects.values('id'): xml.append(f'  <url><loc>{base}/product/{p["id"]}/</loc><priority>0.8</priority><changefreq>monthly</changefreq></url>')
    xml.append('</urlset>')
    return HttpResponse('\n'.join(xml),content_type='application/xml')

def robots(request):
    base=request.build_absolute_uri('/')
    return HttpResponse('\n'.join(['User-agent: *','Allow: /','Disallow: /admin-panel/','Disallow: /agent/','Disallow: /login/','Disallow: /api/',f'Sitemap: {base}sitemap.xml']),content_type='text/plain')

def error_404(request,exception=None): return render(request,'404.html',status=404)
def error_500(request): return render(request,'404.html',status=500)
