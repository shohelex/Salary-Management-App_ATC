from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Avg, Q
from datetime import date, timedelta
from decimal import Decimal
import calendar

from .models import (FactoryEmployee, FactoryAttendance, MonthlyPerformance,
                     FactorySalary, WeeklyPayment, FactoryLoan)
from .forms import (FactoryEmployeeForm, MonthlyPerformanceForm,
                    SalaryEditForm, FactoryLoanForm, WeeklyPaymentEditForm)


# ─── Employee Views ──────────────────────────────────────────

def employee_list(request):
    employees = FactoryEmployee.objects.all()
    show_inactive = request.GET.get('show_inactive', False)
    if not show_inactive:
        employees = employees.filter(is_active=True)
    return render(request, 'factory/employee_list.html', {
        'employees': employees, 'show_inactive': show_inactive,
    })


def employee_add(request):
    if request.method == 'POST':
        form = FactoryEmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee added successfully!')
            return redirect('factory:employee_list')
    else:
        form = FactoryEmployeeForm()
    return render(request, 'factory/employee_form.html', {'form': form, 'title': 'Add Employee'})


def employee_detail(request, pk):
    employee = get_object_or_404(FactoryEmployee, pk=pk)
    today = date.today()
    cm, cy = today.month, today.year

    # Current month attendance summary
    month_att = FactoryAttendance.objects.filter(employee=employee, date__month=cm, date__year=cy)
    present_days = month_att.filter(Q(status='present') | Q(status='half_day')).count()
    regular_hours = month_att.filter(
        Q(status='present') | Q(status='half_day')
    ).aggregate(total=Sum('working_hours'))['total'] or Decimal('0')
    overtime_hours = month_att.aggregate(total=Sum('overtime_hours'))['total'] or Decimal('0')
    estimated_salary = employee.hourly_rate * (regular_hours + overtime_hours)

    # Weekly payments this month
    month_payments = WeeklyPayment.objects.filter(employee=employee, month=cm, year=cy)
    total_weekly = month_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    running_balance = estimated_salary - total_weekly

    return render(request, 'factory/employee_detail.html', {
        'employee': employee,
        'current_month_name': calendar.month_name[cm],
        'current_year': cy,
        'present_days': present_days,
        'regular_hours': regular_hours,
        'overtime_hours': overtime_hours,
        'estimated_salary': estimated_salary,
        'total_weekly': total_weekly,
        'running_balance': running_balance,
        'recent_attendance': employee.attendances.order_by('-date')[:30],
        'recent_payments': employee.weekly_payments.order_by('-payment_date')[:10],
        'recent_performance': employee.performances.order_by('-year', '-month')[:12],
        'recent_salary': employee.salaries.order_by('-year', '-month')[:6],
        'active_loans': employee.loans.filter(is_active=True),
        'all_loans': employee.loans.all()[:10],
    })


def employee_edit(request, pk):
    employee = get_object_or_404(FactoryEmployee, pk=pk)
    if request.method == 'POST':
        form = FactoryEmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'{employee.name} updated!')
            return redirect('factory:employee_detail', pk=pk)
    else:
        form = FactoryEmployeeForm(instance=employee)
    return render(request, 'factory/employee_form.html', {
        'form': form, 'title': f'Edit {employee.name}', 'employee': employee
    })


def employee_delete(request, pk):
    employee = get_object_or_404(FactoryEmployee, pk=pk)
    if request.method == 'POST':
        name = employee.name
        employee.delete()
        messages.success(request, f'{name} deleted!')
        return redirect('factory:employee_list')
    return render(request, 'factory/employee_confirm_delete.html', {'employee': employee})


# ─── Attendance Views ────────────────────────────────────────

def attendance_list(request):
    selected_date = request.GET.get('date', str(date.today()))
    try:
        filter_date = date.fromisoformat(selected_date)
    except ValueError:
        filter_date = date.today()
    records = FactoryAttendance.objects.filter(date=filter_date).select_related('employee')
    return render(request, 'factory/attendance_list.html', {
        'records': records, 'selected_date': filter_date,
    })


def attendance_add(request):
    if request.method == 'POST':
        att_date = request.POST.get('date', str(date.today()))
        try:
            att_date = date.fromisoformat(att_date)
        except ValueError:
            att_date = date.today()
        employees = FactoryEmployee.objects.filter(is_active=True)
        count = 0
        for emp in employees:
            status = request.POST.get(f'status_{emp.id}', 'absent')
            work_hrs = request.POST.get(f'working_hours_{emp.id}', '8')
            ot_hours = request.POST.get(f'overtime_{emp.id}', '0')
            remarks = request.POST.get(f'remarks_{emp.id}', '')
            try:
                work_hrs = Decimal(work_hrs)
            except (ValueError, TypeError):
                work_hrs = Decimal('8')
            try:
                ot_hours = Decimal(ot_hours)
            except (ValueError, TypeError):
                ot_hours = Decimal('0')
            if status in ('absent', 'leave'):
                work_hrs = Decimal('0')
                ot_hours = Decimal('0')
            elif status == 'half_day' and work_hrs > Decimal('4'):
                work_hrs = Decimal('4')
            FactoryAttendance.objects.update_or_create(
                employee=emp, date=att_date,
                defaults={'status': status, 'working_hours': work_hrs,
                         'overtime_hours': ot_hours, 'remarks': remarks}
            )
            count += 1
        messages.success(request, f'Attendance saved for {count} employees on {att_date}!')
        return redirect('factory:attendance_list')

    employees = FactoryEmployee.objects.filter(is_active=True)
    selected_date_str = request.GET.get('date', str(date.today()))
    try:
        selected_date = date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date = date.today()
    existing = {}
    for rec in FactoryAttendance.objects.filter(date=selected_date, employee__in=employees):
        existing[rec.employee_id] = rec
    employee_data = []
    for emp in employees:
        rec = existing.get(emp.id)
        employee_data.append({
            'employee': emp,
            'status': rec.status if rec else 'present',
            'working_hours': rec.working_hours if rec else Decimal('8'),
            'overtime_hours': rec.overtime_hours if rec else Decimal('0'),
            'remarks': rec.remarks if rec else '',
        })
    return render(request, 'factory/attendance_form.html', {
        'employee_data': employee_data, 'selected_date': selected_date,
    })


def attendance_bulk(request):
    return redirect('factory:attendance_add')


# ─── Weekly Payment Views ───────────────────────────────────

def weekly_payment_list(request):
    month = request.GET.get('month', str(date.today().month))
    year = request.GET.get('year', str(date.today().year))
    try:
        month, year = int(month), int(year)
    except ValueError:
        month, year = date.today().month, date.today().year
    payments = WeeklyPayment.objects.filter(
        month=month, year=year
    ).select_related('employee').order_by('-payment_date', 'employee__name')
    employee_totals = payments.values('employee__name', 'employee__id').annotate(
        total=Sum('amount')
    ).order_by('employee__name')
    grand_total = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    return render(request, 'factory/weekly_payment_list.html', {
        'payments': payments, 'employee_totals': employee_totals,
        'grand_total': grand_total,
        'selected_month': month, 'selected_year': year,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
    })


def weekly_payment_add(request):
    if request.method == 'POST':
        payment_date_str = request.POST.get('payment_date', str(date.today()))
        try:
            payment_date = date.fromisoformat(payment_date_str)
        except ValueError:
            payment_date = date.today()
        employees = FactoryEmployee.objects.filter(is_active=True)
        count = 0
        for emp in employees:
            amount = request.POST.get(f'amount_{emp.id}', '0')
            remarks = request.POST.get(f'remarks_{emp.id}', '')
            try:
                amount = Decimal(amount)
            except (ValueError, TypeError):
                amount = Decimal('0')
            if amount > 0:
                WeeklyPayment.objects.create(
                    employee=emp, payment_date=payment_date,
                    amount=amount, month=payment_date.month,
                    year=payment_date.year, remarks=remarks,
                )
                count += 1
        messages.success(request, f'Weekly payment recorded for {count} employees on {payment_date}!')
        return redirect('factory:weekly_payment_list')

    # Default to current/next Thursday
    today = date.today()
    days_to_thu = (3 - today.weekday()) % 7
    default_thu = today if days_to_thu == 0 else today + timedelta(days=days_to_thu)
    selected_date_str = request.GET.get('date', str(default_thu))
    try:
        selected_date = date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date = default_thu

    employees = FactoryEmployee.objects.filter(is_active=True)
    employee_data = []
    for emp in employees:
        month_att = FactoryAttendance.objects.filter(
            employee=emp, date__month=selected_date.month,
            date__year=selected_date.year, date__lte=selected_date
        )
        reg_hrs = month_att.filter(
            Q(status='present') | Q(status='half_day')
        ).aggregate(total=Sum('working_hours'))['total'] or Decimal('0')
        ot_hrs = month_att.aggregate(total=Sum('overtime_hours'))['total'] or Decimal('0')
        earned = emp.hourly_rate * (reg_hrs + ot_hrs)
        paid = WeeklyPayment.objects.filter(
            employee=emp, month=selected_date.month, year=selected_date.year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        employee_data.append({
            'employee': emp, 'earned_so_far': earned,
            'paid_so_far': paid, 'remaining': earned - paid,
        })
    return render(request, 'factory/weekly_payment_form.html', {
        'employee_data': employee_data, 'selected_date': selected_date,
    })


def weekly_payment_edit(request, pk):
    payment = get_object_or_404(WeeklyPayment, pk=pk)
    if request.method == 'POST':
        form = WeeklyPaymentEditForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Payment updated for {payment.employee.name}!')
            return redirect('factory:weekly_payment_list')
    else:
        form = WeeklyPaymentEditForm(instance=payment)
    return render(request, 'factory/weekly_payment_edit.html', {
        'form': form, 'payment': payment,
    })


def weekly_payment_delete(request, pk):
    payment = get_object_or_404(WeeklyPayment, pk=pk)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, f'Payment for {payment.employee.name} deleted!')
        return redirect('factory:weekly_payment_list')
    return render(request, 'factory/weekly_payment_confirm_delete.html', {'payment': payment})


# ─── Loan Views ─────────────────────────────────────────────

def loan_list(request):
    show_all = request.GET.get('show_all', False)
    loans = FactoryLoan.objects.all().select_related('employee') if show_all else \
            FactoryLoan.objects.filter(is_active=True).select_related('employee')
    total_outstanding = FactoryLoan.objects.filter(is_active=True).aggregate(
        total=Sum('remaining_balance')
    )['total'] or Decimal('0')
    return render(request, 'factory/loan_list.html', {
        'loans': loans, 'total_outstanding': total_outstanding, 'show_all': show_all,
    })


def loan_add(request):
    if request.method == 'POST':
        form = FactoryLoanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan recorded successfully!')
            return redirect('factory:loan_list')
    else:
        form = FactoryLoanForm()
    return render(request, 'factory/loan_form.html', {'form': form, 'title': 'Add Loan'})


def loan_edit(request, pk):
    loan = get_object_or_404(FactoryLoan, pk=pk)
    if request.method == 'POST':
        form = FactoryLoanForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.remaining_balance = loan.loan_amount - loan.total_paid
            if loan.remaining_balance <= 0:
                loan.remaining_balance = Decimal('0')
                loan.is_active = False
            loan.save()
            messages.success(request, 'Loan updated!')
            return redirect('factory:loan_list')
    else:
        form = FactoryLoanForm(instance=loan)
    return render(request, 'factory/loan_form.html', {
        'form': form, 'title': f'Edit Loan - {loan.employee.name}', 'loan': loan
    })


def loan_payment(request, pk):
    loan = get_object_or_404(FactoryLoan, pk=pk)
    if request.method == 'POST':
        amount = request.POST.get('amount', '0')
        try:
            amount = Decimal(amount)
        except (ValueError, TypeError):
            amount = Decimal('0')
        if amount > 0:
            loan.make_payment(amount)
            messages.success(request, f'Payment of ৳{amount:,.0f} recorded!')
        return redirect('factory:loan_list')
    return render(request, 'factory/loan_payment.html', {'loan': loan})


def loan_delete(request, pk):
    loan = get_object_or_404(FactoryLoan, pk=pk)
    if request.method == 'POST':
        loan.delete()
        messages.success(request, f'Loan for {loan.employee.name} deleted!')
        return redirect('factory:loan_list')
    return render(request, 'factory/loan_confirm_delete.html', {'loan': loan})


# ─── Performance Views ──────────────────────────────────────

def performance_list(request):
    month = request.GET.get('month', str(date.today().month))
    year = request.GET.get('year', str(date.today().year))
    try:
        month, year = int(month), int(year)
    except ValueError:
        month, year = date.today().month, date.today().year
    records = MonthlyPerformance.objects.filter(month=month, year=year).select_related('employee')
    return render(request, 'factory/performance_list.html', {
        'records': records, 'selected_month': month, 'selected_year': year,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
    })


def performance_add(request):
    if request.method == 'POST':
        form = MonthlyPerformanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Performance record added!')
            return redirect('factory:performance_list')
    else:
        form = MonthlyPerformanceForm()
    return render(request, 'factory/performance_form.html', {'form': form, 'title': 'Add Performance Record'})


def performance_edit(request, pk):
    record = get_object_or_404(MonthlyPerformance, pk=pk)
    if request.method == 'POST':
        form = MonthlyPerformanceForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Performance record updated!')
            return redirect('factory:performance_list')
    else:
        form = MonthlyPerformanceForm(instance=record)
    return render(request, 'factory/performance_form.html', {'form': form, 'title': 'Edit Performance Record'})


def performance_delete(request, pk):
    record = get_object_or_404(MonthlyPerformance, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Performance record deleted!')
    return redirect('factory:performance_list')


# ─── Salary Views ────────────────────────────────────────────

def salary_report(request):
    month = request.GET.get('month', str(date.today().month))
    year = request.GET.get('year', str(date.today().year))
    try:
        month, year = int(month), int(year)
    except ValueError:
        month, year = date.today().month, date.today().year
    salaries = FactorySalary.objects.filter(
        month=month, year=year
    ).select_related('employee').order_by('employee__name')
    total_net = salaries.aggregate(total=Sum('net_salary'))['total'] or Decimal('0')
    total_balance = salaries.aggregate(total=Sum('balance'))['total'] or Decimal('0')
    total_weekly = salaries.aggregate(total=Sum('total_weekly_payments'))['total'] or Decimal('0')
    all_finalized = not salaries.filter(is_finalized=False).exists() if salaries.exists() else False
    return render(request, 'factory/salary_report.html', {
        'salaries': salaries,
        'selected_month': month, 'selected_year': year,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'total_net': total_net, 'total_balance': total_balance,
        'total_weekly': total_weekly, 'all_finalized': all_finalized,
    })


def salary_calculate(request):
    if request.method == 'POST':
        month = int(request.POST.get('month', date.today().month))
        year = int(request.POST.get('year', date.today().year))
        employees = FactoryEmployee.objects.filter(is_active=True)
        count = 0
        for emp in employees:
            att = FactoryAttendance.objects.filter(employee=emp, date__month=month, date__year=year)
            present_count = att.filter(Q(status='present') | Q(status='half_day')).count()
            total_regular = att.filter(
                Q(status='present') | Q(status='half_day')
            ).aggregate(total=Sum('working_hours'))['total'] or Decimal('0')
            total_ot = att.aggregate(total=Sum('overtime_hours'))['total'] or Decimal('0')
            loan_ded = FactoryLoan.objects.filter(
                employee=emp, is_active=True
            ).aggregate(total=Sum('monthly_installment'))['total'] or Decimal('0')

            salary, created = FactorySalary.objects.get_or_create(
                employee=emp, month=month, year=year,
                defaults={'basic_salary': emp.basic_salary}
            )
            if salary.is_finalized:
                continue
            salary.basic_salary = emp.basic_salary
            salary.present_days = present_count
            salary.regular_hours = total_regular
            salary.overtime_hours = total_ot
            salary.loan_deduction = loan_ded
            salary.calculate()
            salary.save()
            count += 1
        messages.success(request, f'Salary calculated for {count} employees for {calendar.month_name[month]} {year}!')
        return redirect(f'/factory/salary/?month={month}&year={year}')
    return render(request, 'factory/salary_calculate.html', {
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'current_month': date.today().month, 'current_year': date.today().year,
    })


def salary_edit(request, pk):
    salary = get_object_or_404(FactorySalary, pk=pk)
    bonus_suggestion = salary.basic_salary / 2
    if request.method == 'POST':
        form = SalaryEditForm(request.POST, instance=salary)
        if form.is_valid():
            salary = form.save(commit=False)
            salary.calculate()
            salary.save()
            messages.success(request, f'Salary updated for {salary.employee.name}!')
            return redirect(f'/factory/salary/?month={salary.month}&year={salary.year}')
    else:
        form = SalaryEditForm(instance=salary)
    return render(request, 'factory/salary_edit.html', {
        'form': form, 'salary': salary, 'bonus_suggestion': bonus_suggestion,
    })


def salary_delete(request, pk):
    salary = get_object_or_404(FactorySalary, pk=pk)
    if request.method == 'POST':
        month, year = salary.month, salary.year
        salary.delete()
        messages.success(request, f'Salary record for {salary.employee.name} deleted!')
        return redirect(f'/factory/salary/?month={month}&year={year}')
    return render(request, 'factory/salary_confirm_delete.html', {'salary': salary})


def salary_finalize(request):
    """Finalize month: process loan installments, handle negative balances."""
    if request.method == 'POST':
        month = int(request.POST.get('month', date.today().month))
        year = int(request.POST.get('year', date.today().year))
        salaries = FactorySalary.objects.filter(
            month=month, year=year, is_finalized=False
        ).select_related('employee')
        processed = 0
        for salary in salaries:
            if salary.loan_deduction > 0:
                active_loans = FactoryLoan.objects.filter(
                    employee=salary.employee, is_active=True
                ).order_by('loan_date')
                remaining = salary.loan_deduction
                for loan in active_loans:
                    if remaining <= 0:
                        break
                    payment = min(remaining, loan.remaining_balance)
                    loan.make_payment(payment)
                    remaining -= payment
            if salary.balance < 0:
                excess = abs(salary.balance)
                FactoryLoan.objects.create(
                    employee=salary.employee, loan_date=date.today(),
                    loan_amount=excess, monthly_installment=excess,
                    remaining_balance=excess, is_active=True,
                    remarks=f"Excess advance - {calendar.month_name[month]} {year}",
                )
            salary.is_finalized = True
            salary.save()
            processed += 1
        messages.success(request, f'Finalized salary for {processed} employees!')
        return redirect(f'/factory/salary/?month={month}&year={year}')
    return redirect('factory:salary_report')


# ─── Increment View ─────────────────────────────────────────

def increment_recommendation(request):
    year = request.GET.get('year', str(date.today().year))
    try:
        year = int(year)
    except ValueError:
        year = date.today().year
    employees = FactoryEmployee.objects.filter(is_active=True)
    recommendations = []
    for emp in employees:
        perfs = MonthlyPerformance.objects.filter(employee=emp, year=year)
        if perfs.exists():
            aq = perfs.aggregate(a=Avg('quality_score'))['a'] or 0
            ap = perfs.aggregate(a=Avg('punctuality_score'))['a'] or 0
            apr = perfs.aggregate(a=Avg('productivity_score'))['a'] or 0
            at = perfs.aggregate(a=Avg('teamwork_score'))['a'] or 0
            overall = (aq + ap + apr + at) / 4
            if overall >= 9: cat, pct, badge = 'Excellent', 15, 'bg-success'
            elif overall >= 7: cat, pct, badge = 'Good', 10, 'bg-primary'
            elif overall >= 5: cat, pct, badge = 'Average', 5, 'bg-warning'
            elif overall >= 3: cat, pct, badge = 'Below Average', 2, 'bg-secondary'
            else: cat, pct, badge = 'Poor', 0, 'bg-danger'
            inc_amt = emp.basic_salary * Decimal(str(pct)) / Decimal('100')
            recommendations.append({
                'employee': emp, 'avg_quality': round(aq, 1), 'avg_punctuality': round(ap, 1),
                'avg_productivity': round(apr, 1), 'avg_teamwork': round(at, 1),
                'overall': round(overall, 1), 'category': cat, 'badge_class': badge,
                'increment_pct': pct, 'increment_amount': inc_amt,
                'new_salary': emp.basic_salary + inc_amt, 'months_evaluated': perfs.count(),
            })
        else:
            recommendations.append({
                'employee': emp, 'overall': 0, 'category': 'No Data',
                'badge_class': 'bg-light text-dark', 'increment_pct': 0,
                'increment_amount': 0, 'new_salary': emp.basic_salary, 'months_evaluated': 0,
            })
    recommendations.sort(key=lambda x: x['overall'], reverse=True)
    return render(request, 'factory/increment_recommendation.html', {
        'recommendations': recommendations, 'selected_year': year,
    })
