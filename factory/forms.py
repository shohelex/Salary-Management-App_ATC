from django import forms
from .models import FactoryEmployee, FactoryAttendance, MonthlyPerformance, FactorySalary, FactoryLoan, WeeklyPayment
from datetime import date
from decimal import Decimal


class FactoryEmployeeForm(forms.ModelForm):
    class Meta:
        model = FactoryEmployee
        fields = ['name', 'position', 'basic_salary', 'phone', 'address', 'join_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Machine Operator'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monthly basic salary'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address'}),
            'join_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MonthlyPerformanceForm(forms.ModelForm):
    class Meta:
        model = MonthlyPerformance
        fields = ['employee', 'month', 'year', 'quality_score', 'punctuality_score',
                  'productivity_score', 'teamwork_score', 'remarks']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.Select(
                choices=[(i, __import__('calendar').month_name[i]) for i in range(1, 13)],
                attrs={'class': 'form-select'}
            ),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'value': date.today().year}),
            'quality_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'punctuality_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'productivity_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'teamwork_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = FactoryEmployee.objects.filter(is_active=True)


class ApplyIncrementForm(forms.Form):
    new_salary = forms.DecimalField(
        max_digits=10, decimal_places=2,
        min_value=Decimal('0'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '100'}),
        label='New Basic Salary'
    )
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Reason for increment'}),
    )

class WeeklyPaymentEditForm(forms.ModelForm):
    class Meta:
        model = WeeklyPayment
        fields = ['payment_date', 'amount', 'remarks']
        widgets = {
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '100', 'min': '0'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
        }


class FactoryAttendanceEditForm(forms.ModelForm):
    class Meta:
        model = FactoryAttendance
        fields = ['date', 'status', 'working_hours', 'overtime_hours', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'working_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '24'}),
            'overtime_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
        }


class SalaryEditForm(forms.ModelForm):
    class Meta:
        model = FactorySalary
        fields = ['bonus']
        labels = {
            'bonus': 'Bonus',
        }
        widgets = {
            'bonus': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class FactoryLoanForm(forms.ModelForm):
    class Meta:
        model = FactoryLoan
        fields = ['employee', 'loan_date', 'loan_amount', 'monthly_installment', 'remarks']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'loan_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'loan_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Total loan amount'}),
            'monthly_installment': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Monthly deduction from salary'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = FactoryEmployee.objects.filter(is_active=True)
