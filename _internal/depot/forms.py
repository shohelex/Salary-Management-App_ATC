from django import forms
from .models import Depot, DepotEmployee, DepotAttendance, DepotSalary, DepotLoan
from datetime import date
from decimal import Decimal


class DepotForm(forms.ModelForm):
    class Meta:
        model = Depot
        fields = ['name', 'location', 'address', 'phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Depot name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City/Area'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DepotEmployeeForm(forms.ModelForm):
    class Meta:
        model = DepotEmployee
        fields = ['depot', 'name', 'position', 'basic_salary', 'phone', 'address', 'join_date', 'is_active']
        widgets = {
            'depot': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'join_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['depot'].queryset = Depot.objects.filter(is_active=True)


class DepotSalaryEditForm(forms.ModelForm):
    class Meta:
        model = DepotSalary
        fields = ['bonus', 'payments_made']
        labels = {
            'bonus': 'Bonus',
            'payments_made': 'Payments Made',
        }
        widgets = {
            'bonus': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payments_made': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class DepotLoanForm(forms.ModelForm):
    class Meta:
        model = DepotLoan
        fields = ['employee', 'loan_date', 'loan_amount', 'monthly_installment', 'remarks']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'loan_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'loan_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'monthly_installment': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = DepotEmployee.objects.filter(is_active=True)


class DepotAttendanceEditForm(forms.ModelForm):
    class Meta:
        model = DepotAttendance
        fields = ['date', 'status', 'night_bill', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'night_bill': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
        }


class DepotApplyIncrementForm(forms.Form):
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
