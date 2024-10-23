"""
URL configuration for financial_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path
from finance import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/', views.main_page, name='main_page'),
    path('fetch/<str:symbol>/', views.fetch_stock_data, name='fetch_stock_data'),
    path('backtest/<str:symbol>/', views.backtest_view, name='backtest'),
    path('predict/<str:symbol>/', views.predict_stock_prices, name='predict_stock_prices'),
    path('report/pdf/<str:symbol>/', views.generate_report, name='generate_report'),
    path('report/json/<str:symbol>/', views.generate_report_json, name='generate_report_json'),
    path('backtest/pdf/<str:symbol>/<str:initial_investment>', views.generate_backtest_report, name='generate_backtest_report'),
    path('backtest/json/<str:symbol>/<str:initial_investment>', views.generate_backtest_json, name='generate_backtest_json'),
]
