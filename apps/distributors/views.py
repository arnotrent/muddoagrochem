from django.shortcuts import render
from django.http import JsonResponse
from apps.distributors.models import Distributor
def distributors(request):
    all_d=Distributor.objects.all()
    regions=Distributor.objects.values_list('region',flat=True).distinct().order_by('region')
    return render(request,'distributors.html',{'distributors':all_d,'regions':regions})
def api_distributors(request):
    qs=Distributor.objects.all()
    r=request.GET.get('region')
    if r: qs=qs.filter(region=r)
    return JsonResponse([{'id':d.id,'name':d.name,'region':d.region,'district':d.district,'address':d.address,'phone':d.phone,'email':d.email,'lat':d.lat,'lng':d.lng} for d in qs],safe=False)
