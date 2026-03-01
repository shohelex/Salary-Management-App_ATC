from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class SalesRecord(models.Model):
    """Sales record for tracking revenue."""
    CATEGORY_CHOICES = [
        ('product_sales', 'Product Sales'),
        ('wholesale', 'Wholesale'),
        ('retail', 'Retail'),
        ('export', 'Export'),
        ('other', 'Other'),
    ]

    date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(
        max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='product_sales')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"Sale: {self.description[:50]} - ৳{self.amount:,.0f}"


class CostRecord(models.Model):
    """Cost record for tracking business costs."""
    CATEGORY_CHOICES = [
        ('raw_materials', 'Raw Materials'),
        ('production', 'Production Cost'),
        ('logistics', 'Logistics & Shipping'),
        ('salary', 'Salary & Wages'),
        ('overhead', 'Overhead'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]

    date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(
        max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='production')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"Cost: {self.description[:50]} - ৳{self.amount:,.0f}"
