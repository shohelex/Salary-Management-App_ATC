from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from datetime import date
from decimal import Decimal
import calendar

from .models import SalesRecord, CostRecord
from .forms import SalesRecordForm, CostRecordForm


def sales_cost(request):
    """Sales vs Cost comparison dashboard."""
    month = request.GET.get('month', str(date.today().month))
    year = request.GET.get('year', str(date.today().year))
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        month = date.today().month
        year = date.today().year

    # Monthly data
    sales = SalesRecord.objects.filter(date__month=month, date__year=year)
    costs = CostRecord.objects.filter(date__month=month, date__year=year)

    total_sales = sales.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_costs = costs.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    profit = total_sales - total_costs
    margin = round(float(profit) / float(total_sales) * 100, 1) if total_sales > 0 else 0

    # Category breakdowns
    sales_by_cat = sales.values('category').annotate(total=Sum('amount')).order_by('-total')
    costs_by_cat = costs.values('category').annotate(total=Sum('amount')).order_by('-total')

    # Yearly totals
    yearly_sales = SalesRecord.objects.filter(date__year=year).aggregate(
        total=Sum('amount'))['total'] or Decimal('0')
    yearly_costs = CostRecord.objects.filter(date__year=year).aggregate(
        total=Sum('amount'))['total'] or Decimal('0')
    yearly_profit = yearly_sales - yearly_costs

    # Monthly chart data for the year
    chart_labels = []
    chart_sales_data = []
    chart_costs_data = []
    chart_profit_data = []
    for m in range(1, 13):
        chart_labels.append(calendar.month_abbr[m])
        ms = SalesRecord.objects.filter(date__month=m, date__year=year).aggregate(
            total=Sum('amount'))['total'] or 0
        mc = CostRecord.objects.filter(date__month=m, date__year=year).aggregate(
            total=Sum('amount'))['total'] or 0
        chart_sales_data.append(float(ms))
        chart_costs_data.append(float(mc))
        chart_profit_data.append(float(ms) - float(mc))

    return render(request, 'finance/sales_cost.html', {
        'selected_month': month,
        'selected_year': year,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'sales_records': sales[:50],
        'cost_records': costs[:50],
        'total_sales': total_sales,
        'total_costs': total_costs,
        'profit': profit,
        'margin': margin,
        'sales_by_cat': sales_by_cat,
        'costs_by_cat': costs_by_cat,
        'yearly_sales': yearly_sales,
        'yearly_costs': yearly_costs,
        'yearly_profit': yearly_profit,
        'chart_labels': chart_labels,
        'chart_sales_data': chart_sales_data,
        'chart_costs_data': chart_costs_data,
        'chart_profit_data': chart_profit_data,
    })


def sales_add(request):
    if request.method == 'POST':
        form = SalesRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sales record added!')
            return redirect('finance:sales_cost')
    else:
        form = SalesRecordForm()
    return render(request, 'finance/record_form.html', {
        'form': form, 'title': 'Add Sales Record', 'record_type': 'sales'
    })


def sales_edit(request, pk):
    record = get_object_or_404(SalesRecord, pk=pk)
    if request.method == 'POST':
        form = SalesRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sales record updated!')
            return redirect('finance:sales_cost')
    else:
        form = SalesRecordForm(instance=record)
    return render(request, 'finance/record_form.html', {
        'form': form, 'title': 'Edit Sales Record', 'record_type': 'sales'
    })


def sales_delete(request, pk):
    record = get_object_or_404(SalesRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Sales record deleted!')
        return redirect('finance:sales_cost')
    return render(request, 'finance/record_confirm_delete.html', {
        'record': record, 'record_type': 'Sales'
    })


def cost_add(request):
    if request.method == 'POST':
        form = CostRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cost record added!')
            return redirect('finance:sales_cost')
    else:
        form = CostRecordForm()
    return render(request, 'finance/record_form.html', {
        'form': form, 'title': 'Add Cost Record', 'record_type': 'costs'
    })


def cost_edit(request, pk):
    record = get_object_or_404(CostRecord, pk=pk)
    if request.method == 'POST':
        form = CostRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cost record updated!')
            return redirect('finance:sales_cost')
    else:
        form = CostRecordForm(instance=record)
    return render(request, 'finance/record_form.html', {
        'form': form, 'title': 'Edit Cost Record', 'record_type': 'costs'
    })


def cost_delete(request, pk):
    record = get_object_or_404(CostRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Cost record deleted!')
        return redirect('finance:sales_cost')
    return render(request, 'finance/record_confirm_delete.html', {
        'record': record, 'record_type': 'Cost'
    })
