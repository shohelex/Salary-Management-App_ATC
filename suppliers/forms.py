from django import forms
from datetime import date
from .models import Supplier, Purchase, Payment


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'address', 'notes', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact person name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any notes'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['supplier', 'date', 'invoice_number', 'product_type', 'unit_type',
                  'unit_price', 'quantity', 'labor_cost', 'transport_cost', 'is_paid', 'remarks']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'INV-001'}),
            'product_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Steel Rod, Cement'}),
            'unit_type': forms.Select(attrs={'class': 'form-select'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0'}),
            'labor_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'transport_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional remarks'}),
        }

    paid_amount = forms.DecimalField(
        required=False, min_value=0, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Amount paid now'}),
        help_text='Leave blank or 0 to pay full amount'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)
        if not self.initial.get('date'):
            self.initial['date'] = date.today()


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['supplier', 'date', 'amount', 'payment_method', 'reference', 'remarks']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Amount in ৳'}),
            'payment_method': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cash, Bank, bKash'}),
            'reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction/Cheque No.'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional remarks'}),
        }

    def __init__(self, *args, **kwargs):
        supplier_id = kwargs.pop('supplier_id', None)
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)
        if supplier_id:
            self.initial['supplier'] = supplier_id
        if not self.initial.get('date'):
            self.initial['date'] = date.today()
