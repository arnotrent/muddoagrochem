from django.urls import path
from apps.core import views
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('track/', views.track, name='track'),
    path('search/', views.search, name='search'),
    path('compare/', views.compare, name='compare'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('robots.txt', views.robots, name='robots'),
    path('api/search/', views.api_search, name='api_search'),
]
