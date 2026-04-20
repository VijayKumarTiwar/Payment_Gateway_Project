from django.db import models
from django.contrib.auth.models import User


class CorporateCategory(models.Model):
    """Corporate-type expense categories for business finance tracking"""
    
    CATEGORY_TYPES = [
        ('REVENUE', 'Revenue'),
        ('OPERATING_EXPENSE', 'Operating Expense'),
        ('CAPITAL_EXPENDITURE', 'Capital Expenditure'),
        ('ADMINISTRATIVE', 'Administrative'),
        ('MARKETING', 'Marketing & Sales'),
        ('HR', 'Human Resources'),
        ('IT', 'Information Technology'),
        ('FINANCIAL', 'Financial'),
        ('TAX', 'Tax & Legal'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=30, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    budget_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Corporate Categories"
        ordering = ['category_type', 'name']
    
    def __str__(self):
        return f"{self.get_category_type_display()} - {self.name}"


class Department(models.Model):
    """Corporate departments for expense tracking"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class PaymentMethod(models.Model):
    """Corporate payment methods (Cards, Bank Accounts, etc.)"""
    METHOD_TYPES = [
        ('BANK', 'Bank Transfer'),
        ('CARD', 'Corporate Card'),
        ('CASH', 'Petty Cash'),
        ('UPI', 'Digital Payment / UPI'),
    ]
    
    name = models.CharField(max_length=100)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    account_details = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    monthly_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_method_type_display()})"

    @property
    def current_month_spend(self):
        from django.utils import timezone
        today = timezone.now()
        return self.transactions.filter(
            date__year=today.year,
            date__month=today.month,
            transaction_type='EXPENSE',
            status='APPROVED'
        ).aggregate(total=models.Sum('amount'))['total'] or 0

    @property
    def limit_utilization(self):
        if self.monthly_limit > 0:
            return (self.current_month_spend / self.monthly_limit) * 100
        return 0



class Transaction(models.Model):

    """Financial transactions with corporate categorization"""
    
    TRANSACTION_TYPES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    
    TRANSACTION_STATUS = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('RECONCILED', 'Reconciled'),
    ]
    
    date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(CorporateCategory, on_delete=models.PROTECT, related_name='transactions')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='PENDING')

    reference_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.date} - {self.description} - ${self.amount}"


class Budget(models.Model):
    """Annual budget tracking by category and department"""
    fiscal_year = models.IntegerField()
    category = models.ForeignKey(CorporateCategory, on_delete=models.CASCADE, related_name='budgets')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='budgets')
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['fiscal_year', 'category', 'department']
    
    def __str__(self):
        return f"Budget {self.fiscal_year} - {self.category.name} - {self.department.code}"
    
    @property
    def remaining(self):
        return self.allocated_amount - self.spent_amount
    
    @property
    def utilization_percent(self):
        if self.allocated_amount > 0:
            return (self.spent_amount / self.allocated_amount) * 100
        return 0
