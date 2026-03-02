from django.urls import path
from . import views

app_name = 'depot'

urlpatterns = [
    # Depots
    path('', views.depot_list, name='depot_list'),
    path('add/', views.depot_add, name='depot_add'),
    path('<int:pk>/', views.depot_detail, name='depot_detail'),
    path('<int:pk>/edit/', views.depot_edit, name='depot_edit'),
    path('<int:pk>/delete/', views.depot_delete, name='depot_delete'),
    # Employees
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.attendance_add, name='attendance_add'),
    # Salary
    path('salary/', views.salary_report, name='salary_report'),
    path('salary/calculate/', views.salary_calculate, name='salary_calculate'),
    path('salary/finalize/', views.salary_finalize, name='salary_finalize'),
    path('salary/<int:pk>/edit/', views.salary_edit, name='salary_edit'),
    # Loans
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/add/', views.loan_add, name='loan_add'),
    path('loans/<int:pk>/edit/', views.loan_edit, name='loan_edit'),
    path('loans/<int:pk>/payment/', views.loan_payment, name='loan_payment'),
]
