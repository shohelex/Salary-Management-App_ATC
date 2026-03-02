from django.contrib import admin
from .models import Depot, DepotEmployee, DepotAttendance, DepotSalary, DepotLoan


@admin.register(Depot)
class DepotAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'phone', 'is_active', 'employee_count']
    list_filter = ['is_active']


@admin.register(DepotEmployee)
class DepotEmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'depot', 'position', 'basic_salary', 'phone', 'is_active']
    list_filter = ['depot', 'is_active']
    search_fields = ['name']


@admin.register(DepotAttendance)
class DepotAttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'night_bill']
    list_filter = ['status', 'date', 'employee__depot']
    search_fields = ['employee__name']
    date_hierarchy = 'date'


@admin.register(DepotLoan)
class DepotLoanAdmin(admin.ModelAdmin):
    list_display = ['employee', 'loan_date', 'loan_amount', 'monthly_installment',
                    'total_paid', 'remaining_balance', 'is_active']
    list_filter = ['is_active', 'employee__depot']
    search_fields = ['employee__name']


@admin.register(DepotSalary)
class DepotSalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'calculated_salary', 'net_salary',
                    'balance', 'is_finalized']
    list_filter = ['month', 'year', 'is_finalized', 'employee__depot']
    search_fields = ['employee__name']
