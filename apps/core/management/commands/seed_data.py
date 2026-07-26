from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.products.models import Product
from apps.inventory.models import Inventory
from apps.distributors.models import Distributor
from apps.agents.models import Agent

PRODUCTS=[
 {'name':'MUDDOSATE 480SL','category':'herbicide','img':'/static/images/product_muddosate.jpg','stock':120,'reorder':20,
  'active_ingredient':'Glyphosate 480 g/l','formulation':'Soluble Liquid (SL)',
  'crops':'All crops pre-plant/directed, Plantations, Couch grass, Kikuyu grass, Non-crop areas',
  'dosage':'3–6 L/ha in 200–400 L water. Annual grasses: 3–4 L/ha. Perennial: 5–6 L/ha.',
  'packing':'100ml, 500ml, 1L, 5L, 20L',
  'description':'Couch grass and Kikuyu grass that keep coming back are exactly what MUDDOSATE was built to end. It travels down through the leaf into the root system, so the weed doesn\'t just wilt — it stops regrowing. MACL\'s best-selling herbicide, and the one most repeat customers ask for by name.'},
 {'name':'MD MAIZE PLUS 40OD','category':'herbicide','img':'/static/images/product_maizeplus.jpg','stock':95,'reorder':15,
  'active_ingredient':'Nicosulfuron 40 g/l','formulation':'Oil Dispersion (OD)',
  'crops':'Maize — selective, safe on the crop at label rates',
  'dosage':'0.5–0.75 L/ha at 2–6 leaf stage of weeds. Maximum 1 L/ha.',
  'packing':'100ml, 250ml, 500ml, 1L, 5L',
  'description':'Spray over standing maize without fear — MD MAIZE PLUS takes out grass and broadleaf weeds while leaving the crop untouched. One post-emergence pass at the 2–6 leaf stage is usually all a maize field needs for the season.'},
 {'name':'MAX 2.4-D 720SL','category':'herbicide','img':'/static/images/product_max24d.jpg','stock':140,'reorder':25,
  'active_ingredient':'2,4-D Dimethylamine salt 720 g/l','formulation':'Soluble Liquid (SL)',
  'crops':'Maize, Wheat, Sorghum, Sugarcane, Rice, Pastures, Plantation crops',
  'dosage':'1.0–2.0 L/ha in 200–400 L water. Apply at 4–6 leaf stage of weeds.',
  'packing':'100ml, 250ml, 500ml, 1L, 5L, 20L',
  'description':'A cereal farmer\'s standby for broadleaf weeds — MAX 2.4-D clears pigweed and similar competitors out of maize, sorghum and rice without setting the crop back. Works fast, priced for the volumes cereal growers actually spray.'},
 {'name':'MD ACELEMECTIN 48EC','category':'pesticide','img':'/static/images/product_acelemectin.jpg','stock':88,'reorder':15,
  'active_ingredient':'Abamectin 18 g/l + Acetamiprid 30 g/l','formulation':'Emulsifiable Concentrate (EC)',
  'crops':'Cotton, Vegetables, Watermelon, Passion Fruit, Tomatoes, Coffee, Beans',
  'dosage':'500 ml–1 L/ha in 200 L water. Begin at first sign of infestation.',
  'packing':'100ml, 250ml, 500ml, 1L',
  'description':'Whitefly, aphids and bollworm rarely show up alone — that\'s why MD ACELEMECTIN pairs two active ingredients in one spray. Passion fruit and watermelon growers reach for this first when a pest problem is spreading fast.'},
 {'name':'MD FOS 48EC','category':'pesticide','img':'/static/images/product_mdfos.jpg','stock':105,'reorder':20,
  'active_ingredient':'Chlorpyrifos 480 g/l','formulation':'Emulsifiable Concentrate (EC)',
  'crops':'Maize, Vegetables, Fruits, Beans, Coffee, Cotton, Tobacco, Groundnuts',
  'dosage':'1–2 L/ha foliar; 3–4 L/ha soil drench in 200–400 L water.',
  'packing':'100ml, 250ml, 500ml, 1L, 5L',
  'description':'Stem borers and army worms hide where sprays don\'t usually reach — MD FOS works both above ground as a foliar spray and below it as a soil drench, so the pest has nowhere left to hide in maize or groundnut fields.'},
 {'name':'M-D FOS 70SC','category':'pesticide','img':'/static/images/product_mdfos70sc.jpg','stock':70,'reorder':15,
  'active_ingredient':'Chlorpyrifos + Cypermethrin (dual-action SC blend)','formulation':'Suspension Concentrate (SC)',
  'crops':'Cabbages, tomatoes, maize and other field/vegetable crops; also for household and public-health pest control',
  'dosage':'Shake well before use. Dilute per label rate in a part-filled spray tank, then top up and agitate before applying as a full-coverage spray.',
  'packing':'100ml, 250ml, 500ml, 1L',
  'description':'The newer, stronger sibling to MD FOS — this dual-action SC blend gives a fast knock-down and then keeps working long after the spray dries. Built for cabbage, tomato and maize pests, but just as at home clearing bed bugs, ants and cockroaches around the house.'},
 {'name':'MD BENZO-MECTIN 5WDG','category':'pesticide','img':'/static/images/product_benzomectin.jpg','stock':45,'reorder':10,
  'active_ingredient':'Emamectin Benzoate 5%','formulation':'Water-Dispersible Granules (WDG)',
  'crops':'Cabbages, broccoli and brassicas, tomatoes, maize, sorghum, leafy greens',
  'dosage':'Pre-dissolve the granules in a small bucket of water before adding to the spray tank. Apply per label rate, targeting early larval stages for best control.',
  'packing':'5g, 10g, 25g sachets',
  'description':'Fall Armyworm and Tuta Absoluta build resistance fast — that\'s exactly what MD Benzo-Mectin is for. Its granules dissolve into a stomach poison that hard-to-kill caterpillars and moths can\'t easily shrug off. Rotate it in with MD FOS so pests never get the chance to adapt to either one.'},
 {'name':'MD THION 350EC','category':'pesticide','img':'/static/images/product_thion.jpg','stock':70,'reorder':12,
  'active_ingredient':'Dimethoate 350 g/l','formulation':'Emulsifiable Concentrate (EC)',
  'crops':'Vegetables, Coffee, Tea, Citrus, Tobacco, Beans, Groundnuts',
  'dosage':'500 ml–1 L/ha in 200–400 L water.',
  'packing':'100ml, 250ml, 500ml, 1L',
  'description':'Moves through the plant\'s sap, not just the surface — so MD THION keeps working against thrips and mites even on the new growth that emerges after spraying. A coffee and citrus grower\'s dependable, budget-friendly option.'},
 {'name':'MD THOATE 40EC','category':'pesticide','img':'/static/images/product_thoate.jpg','stock':62,'reorder':10,
  'active_ingredient':'Dimethoate 400 g/l','formulation':'Emulsifiable Concentrate (EC)',
  'crops':'Coffee, Vegetables, Cotton, Cereals, Tobacco, Tea',
  'dosage':'500 ml/ha in 200–400 L water. Apply at first sign of pest pressure.',
  'packing':'100ml, 500ml, 1L, 5L',
  'description':'A dual-action insecticide and acaricide in one bottle — MD THOATE handles both the sucking insects and the mites that show up together on tea and cotton, so there\'s no need to stock two separate sprays.'},
 {'name':'TOP-LAXLY M 72WP','category':'fungicide','img':'/static/images/product_toplaxym.jpg','stock':115,'reorder':20,
  'active_ingredient':'Metalaxyl-M 4% + Mancozeb 64%','formulation':'Wettable Powder (WP)',
  'crops':'Onions, Tomatoes, French Beans, Watermelon, Potatoes, Peppers, Carrots',
  'dosage':'2.0–2.5 kg/ha in 400–600 L water. Apply every 7–14 days.',
  'packing':'100g, 250g, 500g, 1kg',
  'description':'When downy mildew shows up overnight after heavy rain, TOP-LAXLY M is what our vegetable growers spray first — it moves systemically through the plant to stop the blight already there while protecting new growth.'},
 {'name':'MD TOP LAXLYN 72WP','category':'fungicide','img':'/static/images/product_toplaxlyn.jpg','stock':90,'reorder':15,
  'active_ingredient':'Metalaxyl 8% + Mancozeb 64%','formulation':'Wettable Powder (WP)',
  'crops':'Vegetables, Potatoes, Grapes, Groundnuts, Tobacco',
  'dosage':'2.5 kg/ha in 500 L water. Apply 10–14 days before expected disease pressure.',
  'packing':'250g, 500g, 1kg',
  'description':'Spray this one ahead of the rains, not after — MD TOP LAXLYN is built for growers who plan for downy mildew and Alternaria blight before symptoms appear, giving potato and grape crops a head start on disease season.'},
 {'name':'TOPLAXLY 72WP','category':'fungicide','img':'/static/images/product_toplaxly.jpg','stock':80,'reorder':15,
  'active_ingredient':'Cymoxanil 8% + Mancozeb 64%','formulation':'Wettable Powder (WP)',
  'crops':'Potatoes, Tomatoes, Cucurbits, Tobacco',
  'dosage':'2.0–2.5 kg/ha. Preventative: every 7–10 days.',
  'packing':'100g, 250g, 500g, 1kg',
  'description':'Late blight can wipe out a tomato or potato field within days — TOPLAXLY combines a fast-acting curative with a protective shield, so it stops an active outbreak and guards the untouched plants around it in the same spray.'},
 {'name':'UREA 46%N','category':'other','img':'/static/images/product_urea.jpg','stock':200,'reorder':40,
  'active_ingredient':'Nitrogen (N) 46%','formulation':'Prilled Granular',
  'crops':'Maize, Rice, Vegetables, Coffee, Sugarcane, Wheat, all field crops',
  'dosage':'50–200 kg/ha. Top-dress in split applications. Do not apply to wet foliage.',
  'packing':'1 kg, 5 kg, 25 kg, 50 kg bags',
  'description':'When a field looks pale and growth has stalled, this is usually the fix — at 46% nitrogen it\'s the most concentrated top-dress fertilizer we stock, pushing visible leaf growth within days on maize, rice and sugarcane.'},
 {'name':'NPK 17:17:17','category':'other','img':'/static/images/product_npk.jpg','stock':180,'reorder':30,
  'active_ingredient':'N 17% + P2O5 17% + K2O 17%','formulation':'Compound Granular',
  'crops':'All crops — maize, vegetables, coffee, tea, sugarcane, horticulture',
  'dosage':'200–400 kg/ha basal application at or before planting.',
  'packing':'1 kg, 5 kg, 25 kg, 50 kg bags',
  'description':'One bag, three nutrients, equal amounts — NPK 17:17:17 is the basal fertilizer growers apply at planting when they want strong roots and even growth without having to blend separate nitrogen, phosphorus and potash bags themselves.'},
 {'name':'FOLIAR BOOST 20-20-20+TE','category':'other','img':'/static/images/product_foliarboost.jpg','stock':95,'reorder':15,
  'active_ingredient':'N 20% + P2O5 20% + K2O 20% + Zn, Fe, Mn, B, Cu','formulation':'Water Soluble Powder',
  'crops':'Vegetables, Flowers, Fruits, Coffee, Tea, Greenhouse crops',
  'dosage':'3–5 g/L foliar spray; 2–5 kg/ha through drip irrigation.',
  'packing':'250g, 500g, 1 kg, 5 kg',
  'description':'When a crop shows yellowing that soil fertilizer alone won\'t fix, this dissolves straight into the spray tank and gets absorbed through the leaf within hours — the trace elements (zinc, iron, manganese) are what a NPK bag alone can\'t give a stressed greenhouse crop.'},
 {'name':'KNAPSACK SPRAYER 16L','category':'other','img':'/static/images/product_sprayer.jpg','stock':35,'reorder':5,
  'active_ingredient':'N/A — Equipment','formulation':'Manual Knapsack Sprayer',
  'crops':'All field, vegetable and plantation spray applications',
  'dosage':'16-litre tank. Operating pressure: 2–4 bar. Adjustable flat fan nozzle.',
  'packing':'Per unit',
  'description':'The sprayer that outlasts a season of daily use — a 16-litre tank, padded straps for the long walk down a row, and an anti-drip nozzle so chemical doesn\'t leak onto your hands between plants. Sold and serviced at every MACL outlet.'},
]

DISTRIBUTORS=[
 ('Muddo Agro HQ — Kampala','Central','Kampala','Container Village Nakivubo, Equity Bank Basement V013, P.O Box 25240','0772-507582 / 0702-507582','kulanju_w@yahoo.com',0.3136,32.5811),
 ('Nakasero Agro Supplies','Central','Kampala','Nakasero Market, Stall 47','+256 701 234567','',0.3180,32.5750),
 ('Wakiso District Outlet','Central','Wakiso','Namulanda Trading Centre, Entebbe Road','+256 754 223344','',0.0667,32.4833),
 ('Masaka Agro Store','Central','Masaka','Birch Avenue, Masaka Town','+256 789 990011','',-0.3396,31.7369),
 ('Jinja Agro Distributor','Eastern','Jinja','Main Street, Jinja Town, Plot 45','+256 782 334455','',0.4244,33.2041),
 ('Mbale Farm Supplies','Eastern','Mbale','Republic Street, Mbale, Shop 12','+256 703 445566','',1.0796,34.1753),
 ('Iganga Agricultural Centre','Eastern','Iganga','Market Street, Iganga Town','+256 756 112233','',0.6085,33.4683),
 ('Gulu Northern Branch','Northern','Gulu','Chwa II Road, Gulu Town','+256 772 556677','',2.7748,32.2990),
 ('Lira Agro Centre','Northern','Lira','Obote Avenue, Lira Town','+256 755 889900','',2.2499,32.8998),
 ('Mbarara Western Hub','Western','Mbarara','High Street, Mbarara, Plot 8','+256 786 667788','',-0.6072,30.6545),
 ('Fort Portal Outlet','Western','Kabarole','Bwamba Road, Fort Portal Town','+256 701 778899','',0.6620,30.2750),
]

AGENTS=[
 ('Alice Namukasa','alice','alice@muddo.ug','+256 701 111001','Central','Kampala'),
 ('Robert Opio','robert','robert@muddo.ug','+256 702 222002','Eastern','Jinja'),
 ('Grace Atim','grace','grace@muddo.ug','+256 703 333003','Northern','Gulu'),
 ('Patrick Tendo','patrick','patrick@muddo.ug','+256 704 444004','Western','Mbarara'),
]

class Command(BaseCommand):
    help='Seed real MACL products, distributors and demo agents'
    def add_arguments(self,p): p.add_argument('--force',action='store_true')
    def handle(self,*a,**o):
        force=o['force']
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin','admin@muddo.ug','muddo@admin2024')
            self.stdout.write(self.style.SUCCESS('✓ Admin created (admin / muddo@admin2024)'))
        if not Product.objects.exists() or force:
            if force: Product.objects.all().delete()
            added=0
            for r in PRODUCTS:
                p,created=Product.objects.get_or_create(name=r['name'],defaults={k:r[k] for k in ('category','description','active_ingredient','formulation','crops','dosage','packing') if k in r}|{'image_url':r.get('img','/static/images/products_all.jpg')})
                if created: Inventory.objects.create(product=p,stock_qty=r.get('stock',50),reorder_level=r.get('reorder',10),unit='units'); added+=1
            self.stdout.write(self.style.SUCCESS(f'✓ {added}/{len(PRODUCTS)} products seeded'))
        if not Distributor.objects.exists() or force:
            if force: Distributor.objects.all().delete()
            for r in DISTRIBUTORS: Distributor.objects.get_or_create(name=r[0],defaults={'region':r[1],'district':r[2],'address':r[3],'phone':r[4],'email':r[5],'lat':r[6],'lng':r[7]})
            self.stdout.write(self.style.SUCCESS(f'✓ {len(DISTRIBUTORS)} distributors seeded'))
        if not Agent.objects.exists() or force:
            n=0
            for name,username,email,phone,region,district in AGENTS:
                if not User.objects.filter(username=username).exists():
                    f,*l=name.split(' ',1)
                    u=User.objects.create_user(username,email,'agent@2024',first_name=f,last_name=' '.join(l) if l else '')
                    Agent.objects.create(user=u,phone=phone,region=region,district=district); n+=1
            self.stdout.write(self.style.SUCCESS(f'✓ {n} agents seeded (password: agent@2024)'))
        self.stdout.write(self.style.SUCCESS('\n✅ Done!\n   Run: python manage.py runserver\n   Admin: http://127.0.0.1:8000/login/ → admin / muddo@admin2024'))
