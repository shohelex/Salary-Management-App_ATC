from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

from .models import Supplier, Purchase, Payment
from .forms import SupplierForm, PurchaseForm, PaymentForm


def supplier_dashboard(request):
    """Overview dashboard with insights across all suppliers."""
    today = date.today()
    month_start = today.replace(day=1)

    # Filters
    start_date = request.GET.get('start', '')
    end_date = request.GET.get('end', '')

    # All-time stats
    total_suppliers = Supplier.objects.filter(is_active=True).count()

    all_purchases = Purchase.objects.all()
    all_payments = Payment.objects.all()

    total_all_purchases = all_purchases.aggregate(total=Sum('total_cost'))['total'] or Decimal('0')
    total_all_payments = all_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_outstanding = total_all_purchases - total_all_payments

    # This month stats
    month_purchases = Purchase.objects.filter(date__gte=month_start, date__lte=today)
    month_purchase_total = month_purchases.aggregate(total=Sum('total_cost'))['total'] or Decimal('0')
    month_payments = Payment.objects.filter(date__gte=month_start, date__lte=today)
    month_payment_total = month_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Custom date-range stats
    range_purchase_total = None
    range_payment_total = None
    if start_date and end_date:
        try:
            s = date.fromisoformat(start_date)
            e = date.fromisoformat(end_date)
            range_purchases = Purchase.objects.filter(date__gte=s, date__lte=e)
            range_purchase_total = range_purchases.aggregate(total=Sum('total_cost'))['total'] or Decimal('0')
            range_payments_qs = Payment.objects.filter(date__gte=s, date__lte=e)
            range_payment_total = range_payments_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        except ValueError:
            pass

    # Per-supplier summary (active suppliers with balances)
    suppliers = Supplier.objects.filter(is_active=True).annotate(
        purchase_total=Sum('purchases__total_cost'),
        payment_total=Sum('payments__amount'),
    ).order_by('name')

    # Top suppliers by purchase volume
    top_suppliers = Supplier.objects.annotate(
        purchase_total=Sum('purchases__total_cost')
    ).filter(purchase_total__gt=0).order_by('-purchase_total')[:10]

    # Recent purchases
    recent_purchases = Purchase.objects.select_related('supplier').all()[:10]

    # Recent payments
    recent_payments = Payment.objects.select_related('supplier').all()[:10]

    # Monthly purchase trend (last 6 months)
    chart_labels = []
    chart_purchases = []
    chart_payments = []
    for i in range(5, -1, -1):
        m = (today.month - i - 1) % 12 + 1
        y = today.year - ((today.month - i - 1) < 0)
        if today.month - i <= 0:
            y = today.year - 1
            m = 12 + (today.month - i)
        import calendar
        chart_labels.append(f"{calendar.month_abbr[m]} {y}")
        p_total = Purchase.objects.filter(date__month=m, date__year=y).aggregate(
            total=Sum('total_cost'))['total'] or 0
        pay_total = Payment.objects.filter(date__month=m, date__year=y).aggregate(
            total=Sum('amount'))['total'] or 0
        chart_purchases.append(float(p_total))
        chart_payments.append(float(pay_total))

    return render(request, 'suppliers/dashboard.html', {
        'total_suppliers': total_suppliers,
        'total_all_purchases': total_all_purchases,
        'total_all_payments': total_all_payments,
        'total_outstanding': total_outstanding,
        'month_purchase_total': month_purchase_total,
        'month_payment_total': month_payment_total,
        'range_purchase_total': range_purchase_total,
        'range_payment_total': range_payment_total,
        'start_date': start_date,
        'end_date': end_date,
        'suppliers': suppliers,
        'top_suppliers': top_suppliers,
        'recent_purchases': recent_purchases,
        'recent_payments': recent_payments,
        'chart_labels': chart_labels,
        'chart_purchases': chart_purchases,
        'chart_payments': chart_payments,
    })


# ─── Supplier CRUD ────────────────────────────────────────────────

def supplier_list(request):
    """List all suppliers."""
    show = request.GET.get('show', 'active')
    if show == 'all':
        suppliers = Supplier.objects.all()
    else:
        suppliers = Supplier.objects.filter(is_active=True)

    suppliers = suppliers.annotate(
        purchase_total=Sum('purchases__total_cost'),
        payment_total=Sum('payments__amount'),
    )

    return render(request, 'suppliers/supplier_list.html', {
        'suppliers': suppliers,
        'show': show,
    })


def supplier_add(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('suppliers:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'suppliers/supplier_form.html', {'form': form, 'title': 'Add Supplier'})


def supplier_detail(request, pk):
    """Full ledger view for a single supplier."""
    supplier = get_object_or_404(Supplier, pk=pk)

    # Filters
    start_date = request.GET.get('start', '')
    end_date = request.GET.get('end', '')

    purchases = supplier.purchases.all()
    payments = supplier.payments.all()

    if start_date:
        try:
            s = date.fromisoformat(start_date)
            purchases = purchases.filter(date__gte=s)
            payments = payments.filter(date__gte=s)
        except ValueError:
            pass
    if end_date:
        try:
            e = date.fromisoformat(end_date)
            purchases = purchases.filter(date__lte=e)
            payments = payments.filter(date__lte=e)
        except ValueError:
            pass

    filtered_purchase_total = purchases.aggregate(total=Sum('total_cost'))['total'] or Decimal('0')
    filtered_payment_total = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    # Product type breakdown
    product_breakdown = purchases.values('product_type').annotate(
        total=Sum('total_cost'),
        qty=Sum('quantity'),
        count=Count('id'),
    ).order_by('-total')

    return render(request, 'suppliers/supplier_detail.html', {
        'supplier': supplier,
        'purchases': purchases,
        'payments': payments,
        'filtered_purchase_total': filtered_purchase_total,
        'filtered_payment_total': filtered_payment_total,
        'product_breakdown': product_breakdown,
        'start_date': start_date,
        'end_date': end_date,
    })


def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated!')
            return redirect('suppliers:supplier_detail', pk=pk)
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'suppliers/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})


def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.is_active = False
        supplier.save()
        messages.success(request, f'Supplier "{supplier.name}" deactivated.')
        return redirect('suppliers:supplier_list')
    return render(request, 'suppliers/supplier_confirm_delete.html', {'supplier': supplier})


# ─── Purchase CRUD (Full Log) ─────────────────────────────────────

def purchase_list(request):
    """Full purchase log — like an Excel sheet."""
    supplier_id = request.GET.get('supplier', '')
    start_date = request.GET.get('start', '')
    end_date = request.GET.get('end', '')
    product = request.GET.get('product', '')

    purchases = Purchase.objects.select_related('supplier').all()

    if supplier_id:
        purchases = purchases.filter(supplier_id=supplier_id)
    if product:
        purchases = purchases.filter(product_type__icontains=product)
    if start_date:
        try:
            purchases = purchases.filter(date__gte=date.fromisoformat(start_date))
        except ValueError:
            pass
    if end_date:
        try:
            purchases = purchases.filter(date__lte=date.fromisoformat(end_date))
        except ValueError:
            pass

    total = purchases.aggregate(total=Sum('total_cost'))['total'] or Decimal('0')
    total_material = purchases.aggregate(total=Sum('material_cost'))['total'] or Decimal('0')
    total_labor = purchases.aggregate(total=Sum('labor_cost'))['total'] or Decimal('0')
    total_transport = purchases.aggregate(total=Sum('transport_cost'))['total'] or Decimal('0')

    suppliers = Supplier.objects.filter(is_active=True).order_by('name')

    return render(request, 'suppliers/purchase_list.html', {
        'purchases': purchases[:200],
        'total': total,
        'total_material': total_material,
        'total_labor': total_labor,
        'total_transport': total_transport,
        'suppliers': suppliers,
        'selected_supplier': supplier_id,
        'selected_product': product,
        'start_date': start_date,
        'end_date': end_date,
    })


def purchase_add(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            try:
                purchase = form.save()
                # If paid instantly, auto-create a payment
                if purchase.is_paid:
                    paid_amount = form.cleaned_data.get('paid_amount')
                    # Use entered amount, or full total if blank/zero
                    if not paid_amount or paid_amount <= 0:
                        paid_amount = purchase.total_cost
                    Payment.objects.create(
                        supplier=purchase.supplier,
                        date=purchase.date,
                        amount=paid_amount,
                        payment_method='Paid with invoice',
                        reference=purchase.invoice_number,
                        remarks=f'Instant payment for invoice #{purchase.invoice_number}',
                    )
                messages.success(request, f'Purchase recorded! Total: ৳{purchase.total_cost:,.0f}')
                return redirect('suppliers:purchase_list')
            except Exception as e:
                logger.error(f"Error recording purchase: {e}")
                messages.error(request, 'An error occurred while saving the purchase. Please try again.')
    else:
        form = PurchaseForm()
    return render(request, 'suppliers/purchase_form.html', {'form': form, 'title': 'Add Purchase'})


def purchase_edit(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    old_total = purchase.total_cost
    old_is_paid = purchase.is_paid
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            purchase = form.save()
            messages.success(request, 'Purchase updated!')
            return redirect('suppliers:purchase_list')
    else:
        form = PurchaseForm(instance=purchase)
    return render(request, 'suppliers/purchase_form.html', {'form': form, 'title': 'Edit Purchase'})


def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    if request.method == 'POST':
        purchase.delete()
        messages.success(request, 'Purchase deleted!')
        return redirect('suppliers:purchase_list')
    return render(request, 'suppliers/purchase_confirm_delete.html', {'purchase': purchase})


# ─── Payment CRUD ─────────────────────────────────────────────────

def payment_list(request):
    """Payment history across all suppliers."""
    supplier_id = request.GET.get('supplier', '')
    start_date = request.GET.get('start', '')
    end_date = request.GET.get('end', '')

    payments = Payment.objects.select_related('supplier').all()

    if supplier_id:
        payments = payments.filter(supplier_id=supplier_id)
    if start_date:
        try:
            payments = payments.filter(date__gte=date.fromisoformat(start_date))
        except ValueError:
            pass
    if end_date:
        try:
            payments = payments.filter(date__lte=date.fromisoformat(end_date))
        except ValueError:
            pass

    total = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    suppliers = Supplier.objects.filter(is_active=True).order_by('name')

    return render(request, 'suppliers/payment_list.html', {
        'payments': payments[:200],
        'total': total,
        'suppliers': suppliers,
        'selected_supplier': supplier_id,
        'start_date': start_date,
        'end_date': end_date,
    })


def payment_add(request, supplier_pk=None):
    """Add a payment to a supplier (repay outstanding balance)."""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Payment of ৳{payment.amount:,.0f} to {payment.supplier.name} recorded!')
            return redirect('suppliers:supplier_detail', pk=payment.supplier.pk)
    else:
        form = PaymentForm(supplier_id=supplier_pk)

    # Show outstanding balances for context
    suppliers_with_balance = []
    for s in Supplier.objects.filter(is_active=True):
        unpaid = s.total_unpaid
        if unpaid > 0:
            suppliers_with_balance.append({'name': s.name, 'id': s.pk, 'unpaid': unpaid})

    return render(request, 'suppliers/payment_form.html', {
        'form': form,
        'title': 'Make Payment',
        'suppliers_with_balance': suppliers_with_balance,
        'supplier_pk': supplier_pk,
    })


def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment updated!')
            return redirect('suppliers:payment_list')
    else:
        form = PaymentForm(instance=payment)
    return render(request, 'suppliers/payment_form.html', {'form': form, 'title': 'Edit Payment'})


def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        supplier_pk = payment.supplier.pk
        payment.delete()
        messages.success(request, 'Payment deleted!')
        return redirect('suppliers:supplier_detail', pk=supplier_pk)
    return render(request, 'suppliers/payment_confirm_delete.html', {'payment': payment})
