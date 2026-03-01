from django import forms
from .models import Expense
from datetime import date


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['expense_type', 'depot', 'date', 'category', 'description', 'amount']
        widgets = {
            'expense_type': forms.Select(attrs={'class': 'form-select', 'onchange': 'toggleDepot(this)'}),
            'depot': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Describe the expense'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Amount in ৳'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from depot.models import Depot
        self.fields['depot'].queryset = Depot.objects.filter(is_active=True)
        self.fields['depot'].required = False
        if not self.initial.get('date'):
            self.initial['date'] = date.today()
