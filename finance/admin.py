from django.contrib import admin
from .models import CorporateCategory, Department, Transaction, Budget, PaymentMethod


@admin.register(CorporateCategory)
class CorporateCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'budget_limit', 'is_active']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['category_type', 'name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'budget', 'manager', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    ordering = ['code']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'method_type', 'monthly_limit', 'expiry_date', 'is_active')
    list_filter = ('method_type', 'is_active')

    search_fields = ('name',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'transaction_type', 'description', 'amount', 'category', 'department', 'payment_method', 'status', 'created_by']
    list_filter = ['transaction_type', 'status', 'category__category_type', 'payment_method', 'date']
    search_fields = ['description', 'reference_number', 'notes']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['fiscal_year', 'category', 'department', 'allocated_amount', 'spent_amount', 'remaining', 'utilization_percent']
    list_filter = ['fiscal_year', 'department']
    search_fields = ['category__name', 'department__name']
    ordering = ['-fiscal_year', 'department__code']
