from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Supplier(models.Model):
    """A supplier from whom raw materials are purchased."""
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_purchases(self):
        """Total of all purchase invoices."""
        return self.purchases.aggregate(
            total=models.Sum('total_cost')
        )['total'] or Decimal('0')

    @property
    def total_paid(self):
        """Total of all payments made to this supplier."""
        return self.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')

    @property
    def total_unpaid(self):
        """Outstanding balance = total purchases - total paid."""
        return self.total_purchases - self.total_paid


class Purchase(models.Model):
    """A purchase invoice from a supplier — full log entry."""
    UNIT_CHOICES = [
        ('piece', 'Per Piece'),
        ('kg', 'Per KG'),
        ('ton', 'Per Ton'),
        ('bag', 'Per Bag'),
        ('liter', 'Per Liter'),
        ('meter', 'Per Meter'),
        ('feet', 'Per Feet'),
        ('bundle', 'Per Bundle'),
        ('other', 'Other'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    date = models.DateField()
    invoice_number = models.CharField(max_length=100, blank=True)
    product_type = models.CharField(max_length=200)
    unit_type = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Price per piece/kg/unit'
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    material_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Auto-calculated: unit_price × quantity'
    )
    labor_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    transport_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))]
    )
    total_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text='material_cost + labor_cost + transport_cost'
    )
    is_paid = models.BooleanField(default=False, help_text='Was this paid instantly?')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"INV#{self.invoice_number} - {self.supplier.name} - {self.product_type}"

    def calculate_costs(self):
        """Calculate material cost and total cost."""
        self.material_cost = self.unit_price * self.quantity
        self.total_cost = self.material_cost + self.labor_cost + self.transport_cost

    def save(self, *args, **kwargs):
        self.calculate_costs()
        super().save(*args, **kwargs)


class Payment(models.Model):
    """A payment made to a supplier against outstanding balance."""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField()
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    payment_method = models.CharField(max_length=50, blank=True, help_text='e.g. Cash, Bank Transfer, bKash')
    reference = models.CharField(max_length=100, blank=True, help_text='Transaction ID or cheque number')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"Payment to {self.supplier.name} - ৳{self.amount:,.0f}"
