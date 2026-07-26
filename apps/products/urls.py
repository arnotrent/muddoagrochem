from django.urls import path
from apps.products import views
urlpatterns = [
    path('pesticides/', views.pesticides, name='pesticides'),
    path('herbicides/', views.herbicides, name='herbicides'),
    path('fungicides/', views.fungicides, name='fungicides'),
    path('other-products/', views.other_products, name='other_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/spec-sheet/', views.spec_sheet, name='product_spec_sheet'),
]
