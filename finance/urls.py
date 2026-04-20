from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard_alias'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('reports/', views.reports, name='reports'),
    # API endpoints
    path('api/monthly-data/', views.api_monthly_data, name='api_monthly_data'),
    path('api/category-breakdown/', views.api_category_breakdown, name='api_category_breakdown'),
]