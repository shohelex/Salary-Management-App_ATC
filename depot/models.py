from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Depot(models.Model):
    """Depot / delivery point model."""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.location})"

    @property
    def employee_count(self):
        return self.employees.filter(is_active=True).count()


class DepotEmployee(models.Model):
    """Depot employee model."""
    depot = models.ForeignKey(Depot, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True, default='Delivery Worker')
    basic_salary = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    join_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['depot__name', 'name']

    def __str__(self):
        return f"{self.name} - {self.depot.name}"

    @property
    def daily_rate(self):
        try:
            return self.basic_salary / Decimal('30') if self.basic_salary else Decimal('0')
        except Exception:
            return Decimal('0')

    @property
    def bonus_amount(self):
        try:
            return self.basic_salary / Decimal('2') if self.basic_salary else Decimal('0')
        except Exception:
            return Decimal('0')

    @property
    def total_loan_balance(self):
        return self.loans.filter(is_active=True).aggregate(
            total=models.Sum('remaining_balance')
        )['total'] or Decimal('0')


class DepotAttendance(models.Model):
    """Daily attendance for depot employees."""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('leave', 'Leave'),
    ]
    employee = models.ForeignKey(DepotEmployee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    night_bill = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'employee__name']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.name} - {self.date} ({self.get_status_display()})"


class DepotLoan(models.Model):
    """Loan record for depot employees."""
    employee = models.ForeignKey(DepotEmployee, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateField()
    loan_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('1'))]
    )
    monthly_installment = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Amount deducted from salary each month"
    )
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-loan_date', 'employee__name']

    def __str__(self):
        return f"{self.employee.name} - ৳{self.loan_amount:,.0f} (Rem: ৳{self.remaining_balance:,.0f})"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_balance = self.loan_amount
        super().save(*args, **kwargs)

    def make_payment(self, amount):
        self.total_paid += amount
        self.remaining_balance -= amount
        if self.remaining_balance <= 0:
            self.remaining_balance = Decimal('0')
            self.is_active = False
        self.save()


class DepotSalary(models.Model):
    """Monthly salary record for depot employees."""
    employee = models.ForeignKey(DepotEmployee, on_delete=models.CASCADE, related_name='salaries')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField(validators=[MinValueValidator(2020)])
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    present_days = models.IntegerField(default=0)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    day_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_night_bills = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    calculated_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loan_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          help_text="Loan installment deducted this month")
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payments_made = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_finalized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month', 'employee__name']
        unique_together = ['employee', 'month', 'year']

    def __str__(self):
        return f"{self.employee.name} - {self.month}/{self.year}"

    def calculate(self):
        try:
            self.daily_rate = self.basic_salary / Decimal('30') if self.basic_salary else Decimal('0')
            self.day_salary = self.daily_rate * Decimal(str(self.present_days))
            self.calculated_salary = self.day_salary + self.total_night_bills
            self.net_salary = (self.calculated_salary + self.bonus
                              - self.loan_deduction)
            self.balance = self.net_salary - self.payments_made
        except Exception as e:
            logger.error(f"Error calculating salary for {self.employee}: {e}")
            raise
