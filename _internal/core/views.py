from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from decimal import Decimal


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
