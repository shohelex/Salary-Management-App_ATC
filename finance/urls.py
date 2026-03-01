from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.sales_cost, name='sales_cost'),
    path('sales/add/', views.sales_add, name='sales_add'),
    path('sales/<int:pk>/edit/', views.sales_edit, name='sales_edit'),
    path('sales/<int:pk>/delete/', views.sales_delete, name='sales_delete'),
    path('costs/add/', views.cost_add, name='cost_add'),
    path('costs/<int:pk>/edit/', views.cost_edit, name='cost_edit'),
    path('costs/<int:pk>/delete/', views.cost_delete, name='cost_delete'),
]
