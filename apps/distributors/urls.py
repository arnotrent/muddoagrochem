from django.urls import path
from apps.distributors import views
urlpatterns = [
    path('distributors/', views.distributors, name='distributors'),
    path('api/distributors/', views.api_distributors, name='api_distributors'),
]
