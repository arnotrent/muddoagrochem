from django.urls import path
from apps.analytics import views
urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('products/', views.admin_products, name='admin_products'),
    path('products/add/', views.admin_add_product, name='admin_add_product'),
    path('products/<int:pid>/edit/', views.admin_edit_product, name='admin_edit_product'),
    path('products/<int:pid>/delete/', views.admin_delete_product, name='admin_delete_product'),
    path('requests/', views.admin_requests, name='admin_requests'),
    path('requests/<int:rid>/update/', views.admin_update_request, name='admin_update_request'),
    path('distributors/', views.admin_distributors, name='admin_distributors'),
    path('distributors/add/', views.admin_add_distributor, name='admin_add_distributor'),
    path('distributors/<int:did>/edit/', views.admin_edit_distributor, name='admin_edit_distributor'),
    path('distributors/<int:did>/delete/', views.admin_delete_distributor, name='admin_delete_distributor'),
    path('inventory/', views.admin_inventory, name='admin_inventory'),
    path('inventory/update/', views.admin_update_inventory, name='admin_update_inventory'),
    path('newsletter/', views.admin_newsletter, name='admin_newsletter'),
    path('import/', views.admin_import, name='admin_import'),
    path('settings/', views.admin_settings, name='admin_settings'),
    path('api/analytics/', views.api_analytics, name='api_analytics'),
]
