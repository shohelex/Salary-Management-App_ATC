from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Expense(models.Model):
    """Daily expense tracking for factory and depots."""
    EXPENSE_TYPE_CHOICES = [
        ('factory', 'Factory'),
        ('depot', 'Depot'),
    ]
    CATEGORY_CHOICES = [
        ('raw_materials', 'Raw Materials'),
        ('utilities', 'Utilities (Electric/Water/Gas)'),
        ('transport', 'Transport'),
        ('maintenance', 'Maintenance & Repairs'),
        ('fuel', 'Fuel'),
        ('food', 'Food & Refreshments'),
        ('office', 'Office Supplies'),
        ('salary_advance', 'Salary Advance'),
        ('loading', 'Loading/Unloading'),
        ('rent', 'Rent'),
        ('miscellaneous', 'Miscellaneous'),
        ('other', 'Other'),
    ]

    expense_type = models.CharField(max_length=10, choices=EXPENSE_TYPE_CHOICES)
    depot = models.ForeignKey(
        'depot.Depot', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='expenses',
        help_text="Select depot if expense type is Depot"
    )
    date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='miscellaneous')
    description = models.TextField()
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.get_expense_type_display()} - {self.description[:50]} (৳{self.amount:,.0f})"
