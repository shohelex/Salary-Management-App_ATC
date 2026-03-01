from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from datetime import date, timedelta
from decimal import Decimal

from .models import Expense
from .forms import ExpenseForm


def expense_list(request):
    """List expenses with filters."""
    expense_type = request.GET.get('type', '')
    start_date = request.GET.get('start', '')
    end_date = request.GET.get('end', '')
    category = request.GET.get('category', '')

    expenses = Expense.objects.all()

    if expense_type:
        expenses = expenses.filter(expense_type=expense_type)
    if category:
        expenses = expenses.filter(category=category)

    if start_date:
        try:
            expenses = expenses.filter(date__gte=date.fromisoformat(start_date))
        except ValueError:
            pass
    if end_date:
        try:
            expenses = expenses.filter(date__lte=date.fromisoformat(end_date))
        except ValueError:
            pass

    total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Category breakdown
    category_totals = expenses.values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')

    return render(request, 'expenses/expense_list.html', {
        'expenses': expenses[:100],
        'total': total,
        'category_totals': category_totals,
        'selected_type': expense_type,
        'selected_category': category,
        'start_date': start_date,
        'end_date': end_date,
        'categories': Expense.CATEGORY_CHOICES,
    })


def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Add Expense'})


def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated!')
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Edit Expense'})


def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted!')
        return redirect('expenses:expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})
