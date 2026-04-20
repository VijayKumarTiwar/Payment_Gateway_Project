from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from .models import CorporateCategory, Department, Transaction, Budget, PaymentMethod
from .ml_engine import get_expense_forecast, detect_anomalies
import json


@login_required
def dashboard(request):
    """Main dashboard with financial overview and charts"""
    today = timezone.now().date()
    current_year = today.year
    
    # Summary statistics
    total_income = Transaction.objects.filter(
        transaction_type='INCOME', 
        status__in=['APPROVED', 'RECONCILED']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_expenses = Transaction.objects.filter(
        transaction_type='EXPENSE', 
        status__in=['APPROVED', 'RECONCILED']
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    net_balance = total_income - total_expenses
    
    # Monthly data for chart (last 6 months)
    six_months_ago = today - timedelta(days=180)
    monthly_data = []
    
    for i in range(6):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        
        income = Transaction.objects.filter(
            transaction_type='INCOME',
            date__gte=month_start,
            date__lt=month_end,
            status__in=['APPROVED', 'RECONCILED']
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expense = Transaction.objects.filter(
            transaction_type='EXPENSE',
            date__gte=month_start,
            date__lt=month_end,
            status__in=['APPROVED', 'RECONCILED']
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%b'),
            'income': float(income),
            'expense': float(expense)
        })
    
    monthly_data.reverse()
    
    # Category breakdown for pie chart
    category_expenses = Transaction.objects.filter(
        transaction_type='EXPENSE',
        status__in=['APPROVED', 'RECONCILED']
    ).values('category__name', 'category__category_type').annotate(
        total=Sum('amount')
    ).order_by('-total')[:8]
    
    # Recent transactions
    recent_transactions = Transaction.objects.select_related(
        'category', 'department'
    ).order_by('-date')[:10]
    
    # Budget utilization
    budgets = Budget.objects.filter(
        fiscal_year=current_year
    ).select_related('category', 'department')[:10]
    
    # ML Insights
    forecast_data = get_expense_forecast()
    anomalies = detect_anomalies()
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
        'monthly_data': json.dumps(monthly_data),
        'category_expenses': category_expenses,
        'recent_transactions': recent_transactions,
        'budgets': budgets,
        'forecast_data': forecast_data,
        'anomalies': anomalies,
        'payment_methods': payment_methods,
    }
    
    return render(request, 'finance/dashboard.html', context)


@login_required
def transaction_list(request):
    """List all transactions with filtering"""
    transactions = Transaction.objects.select_related(
        'category', 'department', 'created_by'
    ).order_by('-date')
    
    # Filters
    trans_type = request.GET.get('type')
    status = request.GET.get('status')
    category_id = request.GET.get('category')
    department_id = request.GET.get('department')
    payment_method_id = request.GET.get('payment_method')
    search = request.GET.get('search')
    
    if trans_type:
        transactions = transactions.filter(transaction_type=trans_type)
    if status:
        transactions = transactions.filter(status=status)
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    if department_id:
        transactions = transactions.filter(department_id=department_id)
    if payment_method_id:
        transactions = transactions.filter(payment_method_id=payment_method_id)
    if search:
        transactions = transactions.filter(
            Q(description__icontains=search) | 
            Q(reference_number__icontains=search)
        )
    
    categories = CorporateCategory.objects.filter(is_active=True)
    departments = Department.objects.filter(is_active=True)
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    context = {
        'transactions': transactions,
        'categories': categories,
        'departments': departments,
        'payment_methods': payment_methods,
        'trans_type': trans_type,
        'status': status,
    }
    
    return render(request, 'finance/transaction_list.html', context)


@login_required
def transaction_create(request):
    """Create new transaction"""
    if request.method == 'POST':
        transaction = Transaction(
            date=request.POST.get('date'),
            transaction_type=request.POST.get('transaction_type'),
            amount=request.POST.get('amount'),
            description=request.POST.get('description'),
            category_id=request.POST.get('category'),
            department_id=request.POST.get('department') or None,
            payment_method_id=request.POST.get('payment_method') or None,
            status=request.POST.get('status', 'PENDING'),
            reference_number=request.POST.get('reference_number'),
            notes=request.POST.get('notes'),
            created_by=request.user
        )
        transaction.save()
        messages.success(request, f'Transaction "{transaction.description}" created successfully.')
        return redirect('transaction_list')
    
    categories = CorporateCategory.objects.filter(is_active=True)
    departments = Department.objects.filter(is_active=True)
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    return render(request, 'finance/transaction_form.html', {
        'categories': categories,
        'departments': departments,
        'payment_methods': payment_methods,
        'action': 'Create'
    })


@login_required
def transaction_edit(request, pk):
    """Edit existing transaction"""
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        transaction.date = request.POST.get('date')
        transaction.transaction_type = request.POST.get('transaction_type')
        transaction.amount = request.POST.get('amount')
        transaction.description = request.POST.get('description')
        transaction.category_id = request.POST.get('category')
        transaction.department_id = request.POST.get('department') or None
        transaction.payment_method_id = request.POST.get('payment_method') or None
        transaction.status = request.POST.get('status', 'PENDING')
        transaction.reference_number = request.POST.get('reference_number')
        transaction.notes = request.POST.get('notes')
        transaction.save()
        messages.success(request, f'Transaction "{transaction.description}" updated successfully.')
        return redirect('transaction_list')
    
    categories = CorporateCategory.objects.filter(is_active=True)
    departments = Department.objects.filter(is_active=True)
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    
    return render(request, 'finance/transaction_form.html', {
        'transaction': transaction,
        'categories': categories,
        'departments': departments,
        'payment_methods': payment_methods,
        'action': 'Edit'
    })


@login_required
def reports(request):
    """Financial reports and analytics"""
    today = timezone.now().date()
    current_year = today.year
    
    # Year-to-date by category type
    category_type_summary = []
    for cat_type, _ in CorporateCategory.CATEGORY_TYPES:
        income = Transaction.objects.filter(
            transaction_type='INCOME',
            category__category_type=cat_type,
            date__year=current_year,
            status__in=['APPROVED', 'RECONCILED']
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expense = Transaction.objects.filter(
            transaction_type='EXPENSE',
            category__category_type=cat_type,
            date__year=current_year,
            status__in=['APPROVED', 'RECONCILED']
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        category_type_summary.append({
            'type': cat_type.replace('_', ' '),
            'income': float(income),
            'expense': float(expense),
            'net': float(income - expense)
        })
    
    # Department summary
    dept_summary = Transaction.objects.filter(
        date__year=current_year,
        status__in=['APPROVED', 'RECONCILED']
    ).values('department__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'category_type_summary': category_type_summary,
        'dept_summary': dept_summary,
        'current_year': current_year,
    }
    
    return render(request, 'finance/reports.html', context)


@login_required
def api_monthly_data(request):
    """API endpoint for monthly chart data"""
    today = timezone.now().date()
    monthly_data = []
    
    for i in range(12):
        month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        
        income = Transaction.objects.filter(
            transaction_type='INCOME',
            date__gte=month_start,
            date__lt=month_end,
            status__in=['APPROVED', 'RECONCILED']
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expense = Transaction.objects.filter(
            transaction_type='EXPENSE',
            date__gte=month_start,
            date__lt=month_end,
            status__in=['APPROVED', 'RECONCILED']
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'income': float(income),
            'expense': float(expense)
        })
    
    monthly_data.reverse()
    return JsonResponse(monthly_data, safe=False)


@login_required
def api_category_breakdown(request):
    """API endpoint for category expense breakdown"""
    expenses = Transaction.objects.filter(
        transaction_type='EXPENSE',
        status__in=['APPROVED', 'RECONCILED']
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')[:10]
    
    data = [{'category': e['category__name'], 'amount': float(e['total'])} for e in expenses]
    return JsonResponse(data, safe=False)
