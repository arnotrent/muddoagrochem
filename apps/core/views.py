import json, random, string
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from apps.core.models import ContactRequest, NewsletterSubscriber
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
    stats_list=[('2020','Year Founded'),(f'{Product.objects.count()}+','Product Lines'),
                (f'{Distributor.objects.count()}+','Distributor Outlets'),('4','Regions Covered')]
    faqs=[
        ('Are your products MAAIF-registered?','Yes. All products distributed by MACL are registered with Uganda\'s Ministry of Agriculture, Animal Industry and Fisheries (MAAIF). Certificates available on request.'),
        ('Do you sell wholesale?','Absolutely. We supply retail and wholesale. Contact us at +256 772 507582 for bulk pricing and distributor partnerships.'),
        ('How do I choose the right product?','Call us or visit our Kampala office. Describe your crop and pest/weed/disease — our team will recommend the right product, dosage and timing.'),
        ('Are your products environmentally safe?','All registered products include environmental safety assessments. Follow label instructions: buffer zones, pre-harvest intervals, and proper PPE.'),
        ('Do you deliver upcountry?','Products available through our 11-outlet nationwide network. Use our Store Locator. For large bulk orders, direct delivery can be arranged.'),
        ('What is the minimum order?','No minimum for retail. For wholesale, minimums vary by product — contact our sales team.'),
        ('How do I report a product problem?','Call +256 772 507582 or email muddoagro811@gmail.com. Keep the product, note the batch number, and describe the issue. We investigate all complaints.'),
        ('What is your return policy?','Sealed, unused products in original packaging may be returned within 7 days with proof of purchase.'),
    ]
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
    return render(request,'about.html',{'stats_list':stats_list,'faqs':faqs,'product_groups':product_groups})

def contact(request):
    if request.method=='POST':
        ref=_ref()
        cr=ContactRequest.objects.create(
            ref_number=ref, name=request.POST.get('name','').strip(),
            email=request.POST.get('email','').strip(), phone=request.POST.get('phone','').strip(),
            subject=request.POST.get('subject','').strip(), message=request.POST.get('message','').strip())
        _send(f'Muddo Agro — Enquiry Received [{ref}]',[cr.email],
              f"Dear {cr.name},\n\nThank you for contacting Muddo Agro Chemicals LTD.\nYour reference: {ref}\n\nWe'll respond within 1 business day.\n\nMuddo Agro Team\n+256 772 507582")
        _send(f'New Enquiry [{ref}] — {cr.subject}',[settings.COMPANY_EMAIL],
              f"From: {cr.name} <{cr.email}>\nPhone: {cr.phone}\nSubject: {cr.subject}\n\n{cr.message}")
        messages.success(request,f'Message sent! Reference: <strong>{ref}</strong> — save it to track your enquiry.')
        return redirect('contact')
    contact_items = [
        ('map-marker-alt','Visit us in Kampala','Container Village Nakivubo, Equity Bank Basement V013, P.O Box 25240',''),
        ('phone','Call or WhatsApp us','<a href="tel:+256772507582">+256 772 507582</a> / <a href="tel:+256702507582">0702-507582</a><br><a href="tel:+256772971620">0772 971620</a> / <a href="tel:+256701971620">0701-971620</a>',''),
        ('envelope','Email the team','<a href="mailto:muddoagro811@gmail.com">muddoagro811@gmail.com</a>',''),
        ('clock','When we\'re open','Monday to Saturday, 8am until 6pm',''),
        ('facebook','Follow along on Facebook','<a href="https://facebook.com/p/MUDDO-AGRO-Chemicals-LTD-100063836929481/" target="_blank">MUDDO AGRO Chemicals LTD</a>',''),
    ]
    return render(request,'contact.html',{'contact_items':contact_items})

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
