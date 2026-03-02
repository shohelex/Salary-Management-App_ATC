from django.contrib import admin
from .models import SalesRecord, CostRecord


@admin.register(SalesRecord)
class SalesRecordAdmin(admin.ModelAdmin):
    list_display = ['date', 'description', 'amount', 'category']
    list_filter = ['category', 'date']
    search_fields = ['description']
    date_hierarchy = 'date'


@admin.register(CostRecord)
class CostRecordAdmin(admin.ModelAdmin):
    list_display = ['date', 'description', 'amount', 'category']
    list_filter = ['category', 'date']
    search_fields = ['description']
    date_hierarchy = 'date'
