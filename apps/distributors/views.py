from django.shortcuts import render
from django.http import JsonResponse
from apps.distributors.models import Distributor

def distributors(request):
    all_d = Distributor.objects.all()
    regions = Distributor.objects.values_list('region', flat=True).distinct().order_by('region')
    countries = Distributor.objects.values_list('country', flat=True).distinct().order_by('country')
    return render(request, 'distributors.html', {'distributors': all_d, 'regions': regions, 'countries': countries})

def api_distributors(request):
    qs = Distributor.objects.all()
    r = request.GET.get('region')
    c = request.GET.get('country')
    if r: qs = qs.filter(region=r)
    if c: qs = qs.filter(country=c)
    return JsonResponse([{
        'id': d.id, 'name': d.name, 'country': d.country, 'region': d.region, 'district': d.district,
        'address': d.address, 'phone': d.phone, 'email': d.email, 'lat': d.lat, 'lng': d.lng,
    } for d in qs], safe=False)
