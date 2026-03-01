from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class FactoryEmployee(models.Model):
    """Factory employee model."""
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True, default='Worker')
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
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (৳{self.basic_salary:,.0f})"

    @property
    def hourly_rate(self):
        return self.basic_salary / Decimal('240')

    @property
    def bonus_amount(self):
        return self.basic_salary / Decimal('2')

    @property
    def total_loan_balance(self):
        return self.loans.filter(is_active=True).aggregate(
            total=models.Sum('remaining_balance')
        )['total'] or Decimal('0')


class FactoryAttendance(models.Model):
    """Daily attendance record for factory employees."""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('leave', 'Leave'),
    ]
    employee = models.ForeignKey(FactoryEmployee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    working_hours = models.DecimalField(
        max_digits=4, decimal_places=1, default=8,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('24'))]
    )
    overtime_hours = models.DecimalField(
        max_digits=4, decimal_places=1, default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'employee__name']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.name} - {self.date} ({self.get_status_display()})"


class WeeklyPayment(models.Model):
    """Weekly advance payment for factory workers (every Thursday)."""
    employee = models.ForeignKey(FactoryEmployee, on_delete=models.CASCADE, related_name='weekly_payments')
    payment_date = models.DateField()
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField(validators=[MinValueValidator(2020)])
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', 'employee__name']

    def __str__(self):
        return f"{self.employee.name} - ৳{self.amount:,.0f} ({self.payment_date})"

    def save(self, *args, **kwargs):
        if self.payment_date:
            self.month = self.payment_date.month
            self.year = self.payment_date.year
        super().save(*args, **kwargs)


class FactoryLoan(models.Model):
    """Loan record for factory employees."""
    employee = models.ForeignKey(FactoryEmployee, on_delete=models.CASCADE, related_name='loans')
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


class MonthlyPerformance(models.Model):
    """Monthly performance record for factory employees."""
    employee = models.ForeignKey(FactoryEmployee, on_delete=models.CASCADE, related_name='performances')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField(validators=[MinValueValidator(2020)])
    quality_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    punctuality_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    productivity_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    teamwork_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-month', 'employee__name']
        unique_together = ['employee', 'month', 'year']

    def __str__(self):
        return f"{self.employee.name} - {self.get_month_display()}/{self.year}"

    def get_month_display(self):
        import calendar
        return calendar.month_name[self.month]

    @property
    def overall_score(self):
        total = self.quality_score + self.punctuality_score + \
                self.productivity_score + self.teamwork_score
        return round(total / 4, 1)


class FactorySalary(models.Model):
    """Monthly salary record for factory employees.

    Flow:
    1. Daily attendance recorded (working_hours + overtime)
    2. Weekly advance payments given every Thursday
    3. Month-end calculation:
       calculated_salary = hourly_rate × (regular_hours + overtime_hours)
       net_salary = calculated_salary + bonuses - deductions - loan_deduction
       balance = net_salary - total_weekly_payments
       If balance < 0 → excess added to employee's loan
    """
    employee = models.ForeignKey(FactoryEmployee, on_delete=models.CASCADE, related_name='salaries')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField(validators=[MinValueValidator(2020)])
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    present_days = models.IntegerField(default=0)
    regular_hours = models.DecimalField(max_digits=8, decimal_places=1, default=0)
    overtime_hours = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    total_hours = models.DecimalField(max_digits=8, decimal_places=1, default=0)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    calculated_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus_1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus_2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    loan_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          help_text="Loan installment deducted this month")
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_weekly_payments = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                   help_text="Positive=owed to worker, Negative=worker owes")
    is_finalized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month', 'employee__name']
        unique_together = ['employee', 'month', 'year']

    def __str__(self):
        return f"{self.employee.name} - {self.month}/{self.year} (৳{self.net_salary:,.0f})"

    def calculate(self):
        self.hourly_rate = self.basic_salary / Decimal('240')
        self.total_hours = self.regular_hours + self.overtime_hours
        self.calculated_salary = self.hourly_rate * self.total_hours
        self.net_salary = (self.calculated_salary + self.bonus_1 + self.bonus_2
                          - self.deductions - self.loan_deduction)
        total_wp = WeeklyPayment.objects.filter(
            employee=self.employee, month=self.month, year=self.year
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')
        self.total_weekly_payments = total_wp
        self.balance = self.net_salary - self.total_weekly_payments
