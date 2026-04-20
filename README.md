# 🏢 Corporate Finance Tracker with AI Insights

A premium, full-stack financial management system built with **Django** and **Machine Learning** to help businesses track revenue, manage department budgets, and forecast future expenses.

![Dashboard Preview](https://via.placeholder.com/1200x600.png?text=Corporate+Finance+Tracker+Dashboard)

## 🚀 Key Features

### 🧠 AI & Predictive Intelligence
- **Expense Forecasting**: Uses Scikit-learn Linear Regression to predict future monthly spending based on historical trends.
- **Anomaly Detection**: Statistical outlier detection to identify unusual spending patterns in specific categories.

### 💳 Payment & Budget Management
- **Payment Method Health**: Real-time monitoring of corporate cards and bank accounts with monthly spending limits and expiry alerts.
- **Departmental Budgeting**: Track budget allocation and utilization across different company departments (Sales, Engineering, etc.).
- **Corporate Categorization**: Advanced categorization including Revenue, Capex, Opex, and Tax-related transactions.

### 📊 Financial Analytics
- **Interactive Dashboard**: Real-time revenue/expense cards, monthly performance charts, and category breakdown.
- **Detailed Reporting**: Year-to-date summaries and department-wise spend analysis.
- **Transaction Management**: Full CRUD system with advanced filtering and search capabilities.

### 🎨 Premium UI/UX
- **Corporate Aesthetics**: Sleek, professional interface using Bootstrap 5.
- **Responsive Design**: Fully functional on desktop, tablet, and mobile.
- **Interactive Charts**: Powered by Chart.js for beautiful data visualization.

## 🛠️ Tech Stack
- **Backend**: Python, Django 6.0
- **Machine Learning**: Scikit-learn, Pandas, NumPy
- **Frontend**: HTML5, Vanilla CSS, Bootstrap 5, Chart.js
- **Database**: SQLite (default)

## 🏁 Getting Started

### 1. Installation
```bash
git clone https://github.com/VijayKumarTiwar/Payment_Gateway_Project.git
cd Payment_Gateway_Project
pip install -r requirements.txt
```

### 2. Database Setup
```bash
python manage.py migrate
python seed_db.py
```

### 3. Run the Server
```bash
python manage.py runserver
```
Access the dashboard at `http://127.0.0.1:8000/`

## 👤 Admin Access
- **Username**: `admin`
- **Password**: `admin123`

---
Built with ❤️ for Corporate Financial Excellence.
