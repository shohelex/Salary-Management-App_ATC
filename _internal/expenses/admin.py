from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['date', 'expense_type', 'category', 'description', 'amount', 'depot']
    list_filter = ['expense_type', 'category', 'date']
    search_fields = ['description']
    date_hierarchy = 'date'
