import os
import django
from django.utils import timezone
from datetime import timedelta
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Finance_Tracker.settings')
django.setup()

from django.contrib.auth.models import User
from finance.models import CorporateCategory, Department, Transaction, Budget, PaymentMethod

def seed_data():
    print("Seeding data...")
    
    # 1. Create Superuser if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser created: admin / admin123")
    
    admin_user = User.objects.get(username='admin')

    # 2. Create Departments
    departments_data = [
        ('Sales & Marketing', 'SALES'),
        ('Engineering', 'ENG'),
        ('Human Resources', 'HR'),
        ('Finance & Accounts', 'FIN'),
        ('Operations', 'OPS'),
    ]
    
    depts = []
    for name, code in departments_data:
        dept, _ = Department.objects.get_or_create(
            code=code, 
            defaults={'name': name, 'budget': random.randint(500000, 2000000)}
        )
        depts.append(dept)
    
    # 3. Create Categories
    categories_data = [
        ('Client Revenue', 'REVENUE', 'Income from project contracts'),
        ('Software Licenses', 'IT', 'Cloud services and tools'),
        ('Office Rent', 'ADMINISTRATIVE', 'Monthly facility cost'),
        ('Employee Salaries', 'HR', 'Monthly payroll'),
        ('Marketing Ads', 'MARKETING', 'Google & LinkedIn ads'),
        ('Hardware Upgrades', 'CAPITAL_EXPENDITURE', 'New laptops and servers'),
        ('Legal Fees', 'TAX', 'Consultation and compliance'),
        ('Interest Earned', 'FINANCIAL', 'Bank interest'),
    ]
    
    cats = []
    for name, cat_type, desc in categories_data:
        cat, _ = CorporateCategory.objects.get_or_create(
            name=name,
            defaults={
                'category_type': cat_type,
                'description': desc,
                'budget_limit': random.randint(100000, 500000)
            }
        )
        cats.append(cat)

    # 4. Create Payment Methods
    methods_data = [
        ('HDFC Bank A/C', 'BANK', 'XXXX-XXXX-1234', 500000, timezone.now().date() + timedelta(days=730)),
        ('Corporate Amex', 'CARD', 'XXXX-XXXX-5678', 200000, timezone.now().date() + timedelta(days=365)),
        ('Petty Cash Box', 'CASH', 'Office Drawer', 50000, None),
        ('Company UPI', 'UPI', 'finance@okcorp', 100000, None),
    ]
    
    methods = []
    for name, m_type, details, limit, expiry in methods_data:
        method, _ = PaymentMethod.objects.update_or_create(
            name=name,
            defaults={
                'method_type': m_type, 
                'account_details': details,
                'monthly_limit': limit,
                'expiry_date': expiry
            }
        )
        methods.append(method)


    
    # 5. Create Budgets
    current_year = timezone.now().year
    for cat in cats:
        if cat.category_type != 'REVENUE':
            for dept in depts:
                Budget.objects.get_or_create(
                    fiscal_year=current_year,
                    category=cat,
                    department=dept,
                    defaults={'allocated_amount': random.randint(50000, 200000)}
                )
    
    # 6. Create Transactions (Last 6 months)
    # Clear old transactions to re-seed with payment methods
    Transaction.objects.all().delete()
    
    today = timezone.now().date()
    descriptions = [
        "AWS Cloud Services", "Google Ads Campaign", "Monthly Payroll - June", 
        "Laptop Purchase for New Joiners", "Office Rent - City Center", 
        "Legal Compliance Audit", "Project Alpha Milestone 1", "Annual Software Renewals"
    ]
    
    for i in range(150):
        days_ago = random.randint(0, 180)
        date = today - timedelta(days=days_ago)
        
        cat = random.choice(cats)
        trans_type = 'INCOME' if cat.category_type in ['REVENUE', 'FINANCIAL'] else 'EXPENSE'
        
        amount = random.randint(5000, 50000)
        if cat.name == 'Employee Salaries':
            amount = random.randint(100000, 300000)
        
        Transaction.objects.create(
            date=date,
            transaction_type=trans_type,
            amount=amount,
            description=random.choice(descriptions),
            category=cat,
            department=random.choice(depts),
            payment_method=random.choice(methods),
            status=random.choice(['APPROVED', 'APPROVED', 'RECONCILED', 'PENDING']),
            reference_number=f"TXN-{random.randint(1000, 9999)}",
            created_by=admin_user
        )
    
    print("Seeding complete!")

if __name__ == '__main__':
    seed_data()
