from django.contrib import admin
from .models import Supplier, Purchase, Payment


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'contact_person', 'phone']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'supplier', 'date', 'product_type', 'quantity', 'total_cost', 'is_paid']
    list_filter = ['is_paid', 'supplier', 'date']
    search_fields = ['invoice_number', 'product_type', 'supplier__name']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'date', 'amount', 'payment_method', 'reference']
    list_filter = ['supplier', 'date']
    search_fields = ['supplier__name', 'reference']
