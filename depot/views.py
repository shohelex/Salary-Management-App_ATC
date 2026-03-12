from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum, Count, Q
from datetime import date
from decimal import Decimal
import calendar
import logging

logger = logging.getLogger(__name__)

from .models import Depot, DepotEmployee, DepotAttendance, DepotSalary, DepotLoan
from .forms import DepotForm, DepotEmployeeForm, DepotSalaryEditForm, DepotLoanForm, DepotAttendanceEditForm, DepotApplyIncrementForm


# ─── Depot Views ─────────────────────────────────────────────

def depot_list(request):
    depots = Depot.objects.all()
    return render(request, 'depot/depot_list.html', {'depots': depots})


def depot_add(request):
    if request.method == 'POST':
        form = DepotForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Depot added!')
            return redirect('depot:depot_list')
    else:
        form = DepotForm()
    return render(request, 'depot/depot_form.html', {'form': form, 'title': 'Add Depot'})


def depot_detail(request, pk):
    depot = get_object_or_404(Depot, pk=pk)
    employees = depot.employees.filter(is_active=True)
    return render(request, 'depot/depot_detail.html', {'depot': depot, 'employees': employees})


def depot_edit(request, pk):
    depot = get_object_or_404(Depot, pk=pk)
    if request.method == 'POST':
        form = DepotForm(request.POST, instance=depot)
        if form.is_valid():
            form.save()
            messages.success(request, f'{depot.name} updated!')
            return redirect('depot:depot_detail', pk=pk)
    else:
        form = DepotForm(instance=depot)
    return render(request, 'depot/depot_form.html', {
        'form': form, 'title': f'Edit {depot.name}', 'depot': depot
    })


def depot_delete(request, pk):
    depot = get_object_or_404(Depot, pk=pk)
    if request.method == 'POST':
        name = depot.name
        depot.delete()
        messages.success(request, f'{name} deleted!')
        return redirect('depot:depot_list')
    return render(request, 'depot/depot_confirm_delete.html', {'depot': depot})


# ─── Depot Employee Views ───────────────────────────────────

def employee_list(request):
    depot_id = request.GET.get('depot', '')
    employees = DepotEmployee.objects.select_related('depot').filter(is_active=True)
    if depot_id:
        employees = employees.filter(depot_id=depot_id)
    depots = Depot.objects.filter(is_active=True)
    return render(request, 'depot/employee_list.html', {
        'employees': employees, 'depots': depots, 'selected_depot': depot_id,
    })


def employee_add(request):
    if request.method == 'POST':
        form = DepotEmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Depot employee added!')
            return redirect('depot:employee_list')
    else:
        form = DepotEmployeeForm()
    return render(request, 'depot/employee_form.html', {'form': form, 'title': 'Add Depot Employee'})


def employee_detail(request, pk):
    employee = get_object_or_404(DepotEmployee, pk=pk)
    return render(request, 'depot/employee_detail.html', {
        'employee': employee,
        'recent_attendance': employee.attendances.order_by('-date')[:30],
        'recent_salary': employee.salaries.order_by('-year', '-month')[:6],
        'active_loans': employee.loans.filter(is_active=True),
        'all_loans': employee.loans.all()[:10],
    })


def employee_edit(request, pk):
    employee = get_object_or_404(DepotEmployee, pk=pk)
    if request.method == 'POST':
        form = DepotEmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'{employee.name} updated!')
            return redirect('depot:employee_detail', pk=pk)
    else:
        form = DepotEmployeeForm(instance=employee)
    return render(request, 'depot/employee_form.html', {
        'form': form, 'title': f'Edit {employee.name}', 'employee': employee
    })


def employee_delete(request, pk):
    employee = get_object_or_404(DepotEmployee, pk=pk)
    if request.method == 'POST':
        name = employee.name
        employee.delete()
        messages.success(request, f'{name} deleted!')
        return redirect('depot:employee_list')
    return render(request, 'depot/employee_confirm_delete.html', {'employee': employee})


# ─── Depot Attendance Views ──────────────────────────────────

def attendance_list(request):
    selected_date = request.GET.get('date', str(date.today()))
    depot_id = request.GET.get('depot', '')
    try:
        filter_date = date.fromisoformat(selected_date)
    except ValueError:
        filter_date = date.today()
    records = DepotAttendance.objects.filter(date=filter_date).select_related('employee', 'employee__depot')
    if depot_id:
        records = records.filter(employee__depot_id=depot_id)
    depots = Depot.objects.filter(is_active=True)
    return render(request, 'depot/attendance_list.html', {
        'records': records, 'selected_date': filter_date,
        'depots': depots, 'selected_depot': depot_id,
    })


def attendance_add(request):
    depot_id = request.GET.get('depot', '') or request.POST.get('depot', '')
    if request.method == 'POST':
        att_date = request.POST.get('date', str(date.today()))
        try:
            att_date = date.fromisoformat(att_date)
        except ValueError:
            att_date = date.today()
        employees = DepotEmployee.objects.filter(depot_id=depot_id, is_active=True) if depot_id else \
                    DepotEmployee.objects.filter(is_active=True)
        count = 0
        for emp in employees:
            status = request.POST.get(f'status_{emp.id}', 'absent')
            night_bill = request.POST.get(f'night_bill_{emp.id}', '0')
            remarks = request.POST.get(f'remarks_{emp.id}', '')
            try:
                night_bill = Decimal(night_bill)
            except (ValueError, TypeError):
                night_bill = Decimal('0')
            DepotAttendance.objects.update_or_create(
                employee=emp, date=att_date,
                defaults={'status': status, 'night_bill': night_bill, 'remarks': remarks}
            )
            count += 1
        messages.success(request, f'Attendance saved for {count} depot employees on {att_date}!')
        return redirect('depot:attendance_list')

    depots = Depot.objects.filter(is_active=True)
    employees = DepotEmployee.objects.filter(is_active=True).select_related('depot')
    if depot_id:
        employees = employees.filter(depot_id=depot_id)
    selected_date_str = request.GET.get('date', str(date.today()))
    try:
        selected_date = date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date = date.today()
    existing = {}
    for rec in DepotAttendance.objects.filter(date=selected_date, employee__in=employees):
        existing[rec.employee_id] = rec
    employee_data = []
    for emp in employees:
        rec = existing.get(emp.id)
        employee_data.append({
            'employee': emp,
            'status': rec.status if rec else 'present',
            'night_bill': rec.night_bill if rec else Decimal('0'),
            'remarks': rec.remarks if rec else '',
        })
    return render(request, 'depot/attendance_form.html', {
        'employee_data': employee_data, 'depots': depots,
        'selected_depot': depot_id, 'selected_date': selected_date,
    })


def attendance_edit(request, pk):
    att = get_object_or_404(DepotAttendance, pk=pk)
    if request.method == 'POST':
        form = DepotAttendanceEditForm(request.POST, instance=att)
        if form.is_valid():
            form.save()
            messages.success(request, f'Attendance updated for {att.employee.name}!')
            return redirect('depot:employee_detail', pk=att.employee.pk)
    else:
        form = DepotAttendanceEditForm(instance=att)
    return render(request, 'depot/attendance_edit.html', {
        'form': form, 'attendance': att,
    })


def attendance_delete(request, pk):
    att = get_object_or_404(DepotAttendance, pk=pk)
    if request.method == 'POST':
        emp_pk = att.employee.pk
        att.delete()
        messages.success(request, f'Attendance record deleted!')
        return redirect('depot:employee_detail', pk=emp_pk)
    return render(request, 'depot/attendance_confirm_delete.html', {'attendance': att})


# ─── Depot Loan Views ───────────────────────────────────────

def loan_list(request):
    show_all = request.GET.get('show_all', False)
    loans = DepotLoan.objects.all().select_related('employee', 'employee__depot') if show_all else \
            DepotLoan.objects.filter(is_active=True).select_related('employee', 'employee__depot')
    total_outstanding = DepotLoan.objects.filter(is_active=True).aggregate(
        total=Sum('remaining_balance')
    )['total'] or Decimal('0')
    return render(request, 'depot/loan_list.html', {
        'loans': loans, 'total_outstanding': total_outstanding, 'show_all': show_all,
    })


def loan_add(request):
    if request.method == 'POST':
        form = DepotLoanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan recorded!')
            return redirect('depot:loan_list')
    else:
        form = DepotLoanForm()
    return render(request, 'depot/loan_form.html', {'form': form, 'title': 'Add Depot Loan'})


def loan_edit(request, pk):
    loan = get_object_or_404(DepotLoan, pk=pk)
    if request.method == 'POST':
        form = DepotLoanForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.remaining_balance = loan.loan_amount - loan.total_paid
            if loan.remaining_balance <= 0:
                loan.remaining_balance = Decimal('0')
                loan.is_active = False
            loan.save()
            messages.success(request, 'Loan updated!')
            return redirect('depot:loan_list')
    else:
        form = DepotLoanForm(instance=loan)
    return render(request, 'depot/loan_form.html', {
        'form': form, 'title': f'Edit Loan - {loan.employee.name}', 'loan': loan
    })


def loan_payment(request, pk):
    loan = get_object_or_404(DepotLoan, pk=pk)
    if request.method == 'POST':
        amount = request.POST.get('amount', '0')
        try:
            amount = Decimal(amount)
        except (ValueError, TypeError):
            amount = Decimal('0')
        if amount > 0:
            loan.make_payment(amount)
            messages.success(request, f'Payment of ৳{amount:,.0f} recorded!')
        return redirect('depot:loan_list')
    return render(request, 'depot/loan_payment.html', {'loan': loan})


def loan_delete(request, pk):
    loan = get_object_or_404(DepotLoan, pk=pk)
    if request.method == 'POST':
        loan.delete()
        messages.success(request, f'Loan for {loan.employee.name} deleted!')
        return redirect('depot:loan_list')
    return render(request, 'depot/loan_confirm_delete.html', {'loan': loan})


# ─── Depot Salary Views ─────────────────────────────────────

def salary_report(request):
    month = request.GET.get('month', str(date.today().month))
    year = request.GET.get('year', str(date.today().year))
    depot_id = request.GET.get('depot', '')
    start_month = request.GET.get('start_month', '')
    end_month = request.GET.get('end_month', '')
    try:
        month, year = int(month), int(year)
    except ValueError:
        month, year = date.today().month, date.today().year

    if start_month and end_month:
        try:
            sm, sy = int(start_month.split('-')[1]), int(start_month.split('-')[0])
            em, ey = int(end_month.split('-')[1]), int(end_month.split('-')[0])
            salaries = DepotSalary.objects.filter(
                year__gte=sy, year__lte=ey
            ).select_related('employee', 'employee__depot')
            salaries = salaries.exclude(year=sy, month__lt=sm).exclude(year=ey, month__gt=em)
        except (ValueError, IndexError):
            salaries = DepotSalary.objects.filter(month=month, year=year).select_related('employee', 'employee__depot')
    else:
        salaries = DepotSalary.objects.filter(month=month, year=year).select_related('employee', 'employee__depot')

    if depot_id:
        salaries = salaries.filter(employee__depot_id=depot_id)
    total_salary = salaries.aggregate(total=Sum('net_salary'))['total'] or Decimal('0')
    total_balance = salaries.aggregate(total=Sum('balance'))['total'] or Decimal('0')
    depots = Depot.objects.filter(is_active=True)
    all_finalized = not salaries.filter(is_finalized=False).exists() if salaries.exists() else False
    return render(request, 'depot/salary_report.html', {
        'salaries': salaries, 'selected_month': month, 'selected_year': year,
        'selected_depot': depot_id,
        'start_month': start_month, 'end_month': end_month,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'total_salary': total_salary, 'total_balance': total_balance,
        'depots': depots, 'all_finalized': all_finalized,
    })


def salary_calculate(request):
    if request.method == 'POST':
        try:
            month = int(request.POST.get('month', date.today().month))
            year = int(request.POST.get('year', date.today().year))
            employees = DepotEmployee.objects.filter(is_active=True)
            count = 0
            for emp in employees:
                try:
                    att = DepotAttendance.objects.filter(employee=emp, date__month=month, date__year=year)
                    present_count = att.filter(Q(status='present') | Q(status='half_day')).count()
                    half_days = att.filter(status='half_day').count()
                    effective_days = present_count - (half_days * Decimal('0.5'))
                    total_night = att.aggregate(total=Sum('night_bill'))['total'] or Decimal('0')
                    loan_ded = DepotLoan.objects.filter(
                        employee=emp, is_active=True
                    ).aggregate(total=Sum('monthly_installment'))['total'] or Decimal('0')

                    salary, created = DepotSalary.objects.get_or_create(
                        employee=emp, month=month, year=year,
                        defaults={'basic_salary': emp.basic_salary}
                    )
                    if salary.is_finalized:
                        continue
                    salary.basic_salary = emp.basic_salary
                    salary.present_days = int(effective_days)
                    salary.total_night_bills = total_night
                    salary.loan_deduction = loan_ded
                    salary.calculate()
                    salary.save()
                    count += 1
                except Exception as e:
                    logger.error(f"Error calculating salary for {emp.name}: {e}")
                    continue
            messages.success(request, f'Salary calculated for {count} depot employees!')
            return redirect(f'/depot/salary/?month={month}&year={year}')
        except Exception as e:
            logger.error(f"Depot salary calculation error: {e}")
            messages.error(request, 'An error occurred during salary calculation. Please try again.')
            return redirect('depot:salary_report')
    return render(request, 'depot/salary_calculate.html', {
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'current_month': date.today().month, 'current_year': date.today().year,
    })


def salary_edit(request, pk):
    salary = get_object_or_404(DepotSalary, pk=pk)
    bonus_suggestion = salary.basic_salary / 2
    if request.method == 'POST':
        form = DepotSalaryEditForm(request.POST, instance=salary)
        if form.is_valid():
            salary = form.save(commit=False)
            salary.calculate()
            salary.save()
            messages.success(request, f'Salary updated for {salary.employee.name}!')
            return redirect(f'/depot/salary/?month={salary.month}&year={salary.year}')
    else:
        form = DepotSalaryEditForm(instance=salary)
    return render(request, 'depot/salary_edit.html', {
        'form': form, 'salary': salary, 'bonus_suggestion': bonus_suggestion,
    })


def salary_delete(request, pk):
    salary = get_object_or_404(DepotSalary, pk=pk)
    if request.method == 'POST':
        month, year = salary.month, salary.year
        salary.delete()
        messages.success(request, f'Salary record for {salary.employee.name} deleted!')
        return redirect(f'/depot/salary/?month={month}&year={year}')
    return render(request, 'depot/salary_confirm_delete.html', {'salary': salary})


def salary_finalize(request):
    if request.method == 'POST':
        try:
            month = int(request.POST.get('month', date.today().month))
            year = int(request.POST.get('year', date.today().year))
            salaries = DepotSalary.objects.filter(
                month=month, year=year, is_finalized=False
            ).select_related('employee')
            processed = 0
            for salary in salaries:
                try:
                    if salary.loan_deduction > 0:
                        active_loans = DepotLoan.objects.filter(
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
                        DepotLoan.objects.create(
                            employee=salary.employee, loan_date=date.today(),
                            loan_amount=excess, monthly_installment=excess,
                            remaining_balance=excess, is_active=True,
                            remarks=f"Excess from {calendar.month_name[month]} {year}",
                        )
                    salary.is_finalized = True
                    salary.save()
                    processed += 1
                except Exception as e:
                    logger.error(f"Error finalizing salary for {salary.employee.name}: {e}")
                    continue
            messages.success(request, f'Finalized salary for {processed} depot employees!')
            return redirect(f'/depot/salary/?month={month}&year={year}')
        except Exception as e:
            logger.error(f"Depot salary finalization error: {e}")
            messages.error(request, 'An error occurred during salary finalization. Please try again.')
            return redirect('depot:salary_report')
    return redirect('depot:salary_report')


# ─── Increment Views ────────────────────────────────────────

def increment_recommendation(request):
    year = request.GET.get('year', str(date.today().year))
    try:
        year = int(year)
    except ValueError:
        year = date.today().year

    employees = DepotEmployee.objects.filter(is_active=True).select_related('depot')
    recommendations = []

    for emp in employees:
        # Attendance stats for the year
        attendance = DepotAttendance.objects.filter(employee=emp, date__year=year)
        total_days = attendance.count()
        present_days = attendance.filter(status__in=['present', 'half_day']).count()
        absent_days = attendance.filter(status='absent').count()
        attendance_rate = round((present_days / total_days * 100), 1) if total_days > 0 else 0

        # Tenure
        tenure_days = (date.today() - emp.join_date).days
        tenure_years = round(tenure_days / 365, 1)

        # Salary history - total earned last year
        salary_records = DepotSalary.objects.filter(employee=emp, year=year)
        months_worked = salary_records.count()

        # Suggestion based on attendance rate and tenure
        if total_days == 0:
            category, suggested_pct, badge = 'No Data', 0, 'bg-light text-dark'
        elif attendance_rate >= 95:
            category, suggested_pct, badge = 'Excellent', 15, 'bg-success'
        elif attendance_rate >= 85:
            category, suggested_pct, badge = 'Good', 10, 'bg-primary'
        elif attendance_rate >= 70:
            category, suggested_pct, badge = 'Average', 5, 'bg-warning'
        elif attendance_rate >= 50:
            category, suggested_pct, badge = 'Below Average', 2, 'bg-secondary'
        else:
            category, suggested_pct, badge = 'Poor', 0, 'bg-danger'

        inc_amt = emp.basic_salary * Decimal(str(suggested_pct)) / Decimal('100')

        recommendations.append({
            'employee': emp,
            'total_days': total_days,
            'present_days': present_days,
            'absent_days': absent_days,
            'attendance_rate': attendance_rate,
            'tenure_years': tenure_years,
            'months_worked': months_worked,
            'category': category,
            'badge_class': badge,
            'increment_pct': suggested_pct,
            'increment_amount': inc_amt,
            'new_salary': emp.basic_salary + inc_amt,
        })

    recommendations.sort(key=lambda x: x['attendance_rate'], reverse=True)
    return render(request, 'depot/increment_recommendation.html', {
        'recommendations': recommendations, 'selected_year': year,
    })


def apply_increment(request, pk):
    employee = get_object_or_404(DepotEmployee, pk=pk)
    year = request.GET.get('year', str(date.today().year))
    try:
        year = int(year)
    except ValueError:
        year = date.today().year

    # Attendance stats for suggestion
    attendance = DepotAttendance.objects.filter(employee=employee, date__year=year)
    total_days = attendance.count()
    present_days = attendance.filter(status__in=['present', 'half_day']).count()
    attendance_rate = round((present_days / total_days * 100), 1) if total_days > 0 else 0
    tenure_years = round((date.today() - employee.join_date).days / 365, 1)

    if total_days == 0:
        category, suggested_pct = 'No Data', 0
    elif attendance_rate >= 95:
        category, suggested_pct = 'Excellent', 15
    elif attendance_rate >= 85:
        category, suggested_pct = 'Good', 10
    elif attendance_rate >= 70:
        category, suggested_pct = 'Average', 5
    elif attendance_rate >= 50:
        category, suggested_pct = 'Below Average', 2
    else:
        category, suggested_pct = 'Poor', 0

    suggested_amount = employee.basic_salary * Decimal(str(suggested_pct)) / Decimal('100')
    suggested_new_salary = employee.basic_salary + suggested_amount

    if request.method == 'POST':
        form = DepotApplyIncrementForm(request.POST)
        if form.is_valid():
            old_salary = employee.basic_salary
            employee.basic_salary = form.cleaned_data['new_salary']
            employee.save()
            diff = employee.basic_salary - old_salary
            messages.success(request, f'Salary updated for {employee.name}: ৳{old_salary:,.0f} → ৳{employee.basic_salary:,.0f} ({("+" if diff >= 0 else "")}{diff:,.0f})')
            return redirect('depot:increment_recommendation')
    else:
        form = DepotApplyIncrementForm(initial={'new_salary': suggested_new_salary})

    return render(request, 'depot/apply_increment.html', {
        'employee': employee, 'form': form, 'year': year,
        'attendance_rate': attendance_rate, 'present_days': present_days,
        'total_days': total_days, 'tenure_years': tenure_years,
        'category': category, 'suggested_pct': suggested_pct,
        'suggested_amount': suggested_amount, 'suggested_new_salary': suggested_new_salary,
    })
