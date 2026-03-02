from django.contrib import admin
from .models import (FactoryEmployee, FactoryAttendance, MonthlyPerformance,
                     FactorySalary, WeeklyPayment, FactoryLoan)


@admin.register(FactoryEmployee)
class FactoryEmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'basic_salary', 'phone', 'join_date', 'is_active']
    list_filter = ['is_active', 'position']
    search_fields = ['name', 'phone']


@admin.register(FactoryAttendance)
class FactoryAttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'working_hours', 'overtime_hours']
    list_filter = ['status', 'date']
    search_fields = ['employee__name']
    date_hierarchy = 'date'


@admin.register(WeeklyPayment)
class WeeklyPaymentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'payment_date', 'amount', 'month', 'year']
    list_filter = ['month', 'year', 'payment_date']
    search_fields = ['employee__name']


@admin.register(FactoryLoan)
class FactoryLoanAdmin(admin.ModelAdmin):
    list_display = ['employee', 'loan_date', 'loan_amount', 'monthly_installment',
                    'total_paid', 'remaining_balance', 'is_active']
    list_filter = ['is_active']
    search_fields = ['employee__name']


@admin.register(MonthlyPerformance)
class MonthlyPerformanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'quality_score', 'punctuality_score',
                    'productivity_score', 'teamwork_score']
    list_filter = ['month', 'year']
    search_fields = ['employee__name']


@admin.register(FactorySalary)
class FactorySalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'calculated_salary', 'net_salary',
                    'total_weekly_payments', 'balance', 'is_finalized']
    list_filter = ['month', 'year', 'is_finalized']
    search_fields = ['employee__name']
