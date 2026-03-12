from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    # Dashboard / Overview
    path('', views.supplier_dashboard, name='supplier_dashboard'),

    # Suppliers CRUD
    path('list/', views.supplier_list, name='supplier_list'),
    path('add/', views.supplier_add, name='supplier_add'),
    path('<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    # Purchases (full log)
    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/add/', views.purchase_add, name='purchase_add'),
    path('purchases/<int:pk>/edit/', views.purchase_edit, name='purchase_edit'),
    path('purchases/<int:pk>/delete/', views.purchase_delete, name='purchase_delete'),

    # Payments
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/add/', views.payment_add, name='payment_add'),
    path('<int:supplier_pk>/pay/', views.payment_add, name='supplier_payment'),
    path('payments/<int:pk>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),
]
