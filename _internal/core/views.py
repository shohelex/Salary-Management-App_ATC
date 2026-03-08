from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import date, timedelta
from decimal import Decimal


# ─── Authentication Views ────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('core:login')


# ─── User Management (Admin Only) ────────────────────────────

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser, login_url='/')(view_func)


@admin_required
def user_list(request):
    users = User.objects.all().order_by('-is_superuser', 'username')
    return render(request, 'core/user_list.html', {'users': users})


@admin_required
def user_create(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        is_admin = request.POST.get('is_admin') == 'on'

        if not username or not password:
            messages.error(request, 'Username and password are required.')
        elif password != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            if is_admin:
                user.is_superuser = True
                user.is_staff = True
                user.save()
            messages.success(request, f'User "{username}" created successfully!')
            return redirect('core:user_list')
    return render(request, 'core/user_form.html', {'title': 'Create User'})


@admin_required
def user_edit(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user_obj.first_name = request.POST.get('first_name', '').strip()
        user_obj.last_name = request.POST.get('last_name', '').strip()
        user_obj.is_active = request.POST.get('is_active') == 'on'
        is_admin = request.POST.get('is_admin') == 'on'
        user_obj.is_superuser = is_admin
        user_obj.is_staff = is_admin

        new_password = request.POST.get('password', '')
        if new_password:
            password2 = request.POST.get('password2', '')
            if new_password != password2:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'core/user_form.html', {
                    'title': 'Edit User', 'edit_user': user_obj,
                })
            user_obj.set_password(new_password)

        user_obj.save()
        messages.success(request, f'User "{user_obj.username}" updated!')
        return redirect('core:user_list')
    return render(request, 'core/user_form.html', {
        'title': 'Edit User', 'edit_user': user_obj,
    })


@admin_required
def user_delete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj == request.user:
        messages.error(request, 'You cannot delete your own account.')
    else:
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f'User "{username}" deleted.')
    return redirect('core:user_list')


@admin_required
def change_password(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        new_password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        if not new_password:
            messages.error(request, 'Password is required.')
        elif new_password != password2:
            messages.error(request, 'Passwords do not match.')
        else:
            user_obj.set_password(new_password)
            user_obj.save()
            messages.success(request, f'Password changed for "{user_obj.username}".')
            return redirect('core:user_list')
    return render(request, 'core/change_password.html', {'edit_user': user_obj})


# ─── Dashboard ───────────────────────────────────────────────

def dashboard(request):
    """Main dashboard view with summary stats."""
    from factory.models import FactoryEmployee, FactoryAttendance
    from depot.models import Depot, DepotEmployee, DepotAttendance
    from expenses.models import Expense
    from finance.models import SalesRecord, CostRecord

    today = date.today()
    current_month = today.month
    current_year = today.year

    # Employee counts
    factory_employees = FactoryEmployee.objects.filter(is_active=True).count()
    depot_employees = DepotEmployee.objects.filter(is_active=True).count()
    total_depots = Depot.objects.filter(is_active=True).count()

    # Today's attendance
    factory_present = FactoryAttendance.objects.filter(
        date=today, status='present'
    ).count()
    factory_absent = factory_employees - factory_present

    depot_present = DepotAttendance.objects.filter(
        date=today, status='present'
    ).count()

    # Monthly expenses
    monthly_factory_expenses = Expense.objects.filter(
        expense_type='factory',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    monthly_depot_expenses = Expense.objects.filter(
        expense_type='depot',
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    total_monthly_expenses = monthly_factory_expenses + monthly_depot_expenses

    # Monthly sales and costs
    monthly_sales = SalesRecord.objects.filter(
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    monthly_costs = CostRecord.objects.filter(
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    profit = monthly_sales - monthly_costs

    # Monthly data for chart (last 6 months)
    chart_labels = []
    chart_sales = []
    chart_costs = []
    chart_expenses = []
    for i in range(5, -1, -1):
        d = today.replace(day=1) - timedelta(days=i * 30)
        month_name = d.strftime('%b %Y')
        chart_labels.append(month_name)

        s = SalesRecord.objects.filter(
            date__month=d.month, date__year=d.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        chart_sales.append(float(s))

        c = CostRecord.objects.filter(
            date__month=d.month, date__year=d.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        chart_costs.append(float(c))

        e = Expense.objects.filter(
            date__month=d.month, date__year=d.year
        ).aggregate(total=Sum('amount'))['total'] or 0
        chart_expenses.append(float(e))

    # Recent expenses
    recent_expenses = Expense.objects.order_by('-date', '-id')[:5]

    context = {
        'factory_employees': factory_employees,
        'depot_employees': depot_employees,
        'total_employees': factory_employees + depot_employees,
        'total_depots': total_depots,
        'factory_present': factory_present,
        'factory_absent': factory_absent,
        'depot_present': depot_present,
        'monthly_factory_expenses': monthly_factory_expenses,
        'monthly_depot_expenses': monthly_depot_expenses,
        'total_monthly_expenses': total_monthly_expenses,
        'monthly_sales': monthly_sales,
        'monthly_costs': monthly_costs,
        'profit': profit,
        'chart_labels': chart_labels,
        'chart_sales': chart_sales,
        'chart_costs': chart_costs,
        'chart_expenses': chart_expenses,
        'recent_expenses': recent_expenses,
        'today': today,
    }
    return render(request, 'core/dashboard.html', context)
