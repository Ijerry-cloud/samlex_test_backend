from django.urls import path
from .views import *

urlpatterns = [
    path('banks/', BankApiView.as_view(), name='get_banks'),
    path('merchants/', MerchantApiView.as_view(), name='get_merchants'),
    path('merchant_summaries/', MerchantSummaryApiView.as_view(), name='get_merchant_summaries'),
    path('bank_summaries/', BankSummaryApiView.as_view(), name='get_bank_summaries'),
    path('bank_summaries/<int:id>/chart/', BankSummaryChartApiView.as_view(), name='get_bank_charts'),
    path('transactions/', TransactionApiView.as_view(), name='get_transactions_view'),
    path('transactions/stats/', ETFTransactionStatView.as_view(), name='get_transaction_stat_view'),
    path('transactions/rule/breakdown/', ETFTransactionRuleBreakdownView.as_view(), name='get_transaction_rule_breakdown'),
    path('transactions/type/breakdown/', ETFTransactionTypeBreakdownView.as_view(), name='get_transaction_type_breakdown'),
    path('transactions/fraud/dashboard/', ETFFraudDashboardView.as_view(), name="fraud_dashboard"),
    path('transactions/rules/', ETFRulesView.as_view(), name="get_create_rules"),
    path('rules/prerequisites/', RulePrerequisitesView.as_view(), name="rule_prerequisites"),
    path('rules/deactivate/', DeactivateRuleView.as_view(), name="deactivate"),
    path('rules/activate/', ActivateRuleView.as_view(), name="activate"),
    path('rules/<int:id>/', EditRuleView.as_view(), name="edit_rule"),
    path('merchants/users/', FetchMerchantsAPIView.as_view(), name="merchants"),
    path('merchants/trends/', GenerateMerchantTrendForLineChart.as_view(), name="merchant_trends"),
    path('merchants/bar/series/', FetchMerchantVolumeForBarPlot.as_view(), name="fetch_merchant_bar_series"),
    path('merchants/pie/activity/', GeneratePieChartActivityAPIView.as_view(), name="generate_merchant_pie_activity"),
    path('merchants/line/differential/', GenerateMerchantDifferentialLineChartAPIView.as_view(), name="generate_merchant_line_differential"),
    path('merchants/monitoring/metric', EditMerchantMonitoringMetricView.as_view(), name="edit_merchant_monitoring_metric"),
    path('sample/', SampleView.as_view(), name="sample")
]

