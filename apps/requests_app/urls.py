from django.urls import path
from apps.requests_app import views
urlpatterns = [
    path('agent/supply-request/', views.agent_supply_request, name='agent_supply_request'),
    path('admin-panel/supply-requests/', views.admin_supply_requests, name='admin_supply_requests'),
    path('admin-panel/supply-requests/<int:rid>/respond/', views.admin_respond_supply, name='admin_respond_supply'),
]
