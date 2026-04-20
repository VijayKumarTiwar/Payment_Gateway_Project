import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from django.db.models import Sum
from .models import Transaction
from datetime import datetime, timedelta

def get_expense_forecast():
    """
    Uses Linear Regression to forecast future expenses based on historical data.
    Returns a list of predicted monthly expenses.
    """
    # 1. Fetch historical expense data
    expenses = Transaction.objects.filter(
        transaction_type='EXPENSE',
        status__in=['APPROVED', 'RECONCILED']
    ).values('date').annotate(total=Sum('amount')).order_by('date')
    
    if not expenses:
        return []
    
    # 2. Convert to Pandas DataFrame
    df = pd.DataFrame(list(expenses))
    df['date'] = pd.to_datetime(df['date'])
    df['total'] = df['total'].astype(float)
    
    # Aggregate by month
    df_monthly = df.resample('ME', on='date').sum().reset_index()
    
    # Need at least 2 months for prediction
    if len(df_monthly) < 2:
        return []
    
    # 3. Prepare data for Linear Regression
    # X = month index (0, 1, 2...)
    # y = total amount
    X = np.array(range(len(df_monthly))).reshape(-1, 1)
    y = df_monthly['total'].values
    
    # 4. Train model
    model = LinearRegression()
    model.fit(X, y)
    
    # 5. Predict next 3 months
    future_X = np.array(range(len(df_monthly), len(df_monthly) + 3)).reshape(-1, 1)
    predictions = model.predict(future_X)
    
    # 6. Format results
    last_date = df_monthly['date'].iloc[-1]
    forecast_results = []
    
    for i, pred in enumerate(predictions):
        future_date = last_date + pd.DateOffset(months=i+1)
        forecast_results.append({
            'month': future_date.strftime('%b %Y'),
            'amount': round(float(max(0, pred)), 2), # Ensure no negative expenses
            'type': 'FORECAST'
        })
        
    return forecast_results

def detect_anomalies():
    """
    Simple statistical anomaly detection for transactions.
    Identifies transactions that are more than 2 standard deviations from the mean for their category.
    """
    anomalies = []
    
    # Fetch all approved/reconciled expenses
    transactions = Transaction.objects.filter(
        transaction_type='EXPENSE',
        status__in=['APPROVED', 'RECONCILED']
    ).select_related('category')
    
    if not transactions:
        return []
    
    df = pd.DataFrame(list(transactions.values('id', 'amount', 'category__name', 'description')))
    if not df.empty:
        df['amount'] = df['amount'].astype(float)
    
    for cat_name in df['category__name'].unique():
        cat_df = df[df['category__name'] == cat_name]
        
        if len(cat_df) < 5: # Need enough data for standard deviation
            continue
            
        mean = cat_df['amount'].mean()
        std = cat_df['amount'].std()
        
        # Threshold: Mean + 2 * STD
        threshold = mean + (2 * std)
        
        cat_anomalies = cat_df[cat_df['amount'] > threshold]
        
        for _, row in cat_anomalies.iterrows():
            anomalies.append({
                'id': row['id'],
                'amount': row['amount'],
                'category': row['category__name'],
                'description': row['description'],
                'reason': f'High deviation from {cat_name} average'
            })
            
    return anomalies
