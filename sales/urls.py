from django.urls import path
from .views import *

urlpatterns = [
    path('sales/', ListCreateSalesView.as_view(), name='create_sales' ),
    path('delete-my-sale/', DeleteSalesView.as_view(), name='create_sales' ),
    path('list-any-sales/', ListAnySalesView.as_view(), name='list_any_sales'),
    path('delete-any-sales/', DeleteAnySaleView.as_view(), name='delete_any_sales'),

    path('daily-report/', DailyReportView.as_view(), name='daily_report'),
    path('customer-summary-report/', CustomerSummaryReportView.as_view(), name='customer-summary'),
    path('employee-summary-report/', EmployeeSummaryReportView.as_view(), name='employee-summary'),
    path('item-inventory/', ItemInventoryView.as_view(), name='item-inventory'),

    path('dashboard-counts/', DashboardGetCountView.as_view(), name='dashboard-counts'),
    path('dashboard-category-charts/', DashboardCategoryChartView.as_view(), name='dashboard-category-charts'),


]