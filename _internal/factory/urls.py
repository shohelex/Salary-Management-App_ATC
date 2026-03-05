from django.urls import path
from . import views

app_name = 'factory'

urlpatterns = [
    # Employees
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.attendance_add, name='attendance_add'),
    path('attendance/<int:pk>/edit/', views.attendance_edit, name='attendance_edit'),
    path('attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
    path('attendance/bulk/', views.attendance_bulk, name='attendance_bulk'),
    # Weekly Payments
    path('weekly-payments/', views.weekly_payment_list, name='weekly_payment_list'),
    path('weekly-payments/add/', views.weekly_payment_add, name='weekly_payment_add'),
    path('weekly-payments/<int:pk>/edit/', views.weekly_payment_edit, name='weekly_payment_edit'),
    path('weekly-payments/<int:pk>/delete/', views.weekly_payment_delete, name='weekly_payment_delete'),
    # Loans
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/add/', views.loan_add, name='loan_add'),
    path('loans/<int:pk>/edit/', views.loan_edit, name='loan_edit'),
    path('loans/<int:pk>/delete/', views.loan_delete, name='loan_delete'),
    path('loans/<int:pk>/payment/', views.loan_payment, name='loan_payment'),
    # Performance
    path('performance/', views.performance_list, name='performance_list'),
    path('performance/add/', views.performance_add, name='performance_add'),
    path('performance/<int:pk>/edit/', views.performance_edit, name='performance_edit'),
    path('performance/<int:pk>/delete/', views.performance_delete, name='performance_delete'),
    # Salary
    path('salary/', views.salary_report, name='salary_report'),
    path('salary/calculate/', views.salary_calculate, name='salary_calculate'),
    path('salary/finalize/', views.salary_finalize, name='salary_finalize'),
    path('salary/<int:pk>/edit/', views.salary_edit, name='salary_edit'),
    path('salary/<int:pk>/delete/', views.salary_delete, name='salary_delete'),
    # Increment
    path('increment/', views.increment_recommendation, name='increment_recommendation'),
    path('increment/<int:pk>/apply/', views.apply_increment, name='apply_increment'),
]
