from django.contrib import admin

from .mixins import ExportCSVMixin
from .models import Bank, BankSummary, Customer, Merchant, MerchantSummary, Terminal, Rule, Product, ETFTransaction, Threshold, ThresholdEmails, MerchantMetric, MerchantMetricEmail


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin, ExportCSVMixin):
    """
    For modifying model representation in Admin
    """

    list_display = ("name", "code")
    list_filter = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    actions = ("export_as_csv",)


@admin.register(BankSummary)
class BankSummaryAdmin(admin.ModelAdmin):
    """
    For modifying model representation in Admin
    """

    list_display = ("bank", "today_val", "txn_val_l30", "txn_val_alltime")


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin, ExportCSVMixin):
    """
    For modifying model representation in Admin
    """

    list_display = ("mid", "name")
    # list_filter = ("mid",)
    search_fields = ("mid", "name")
    ordering = ("name",)
    actions = ("export_as_csv",)


@admin.register(MerchantSummary)
class MerchantSummaryAdmin(admin.ModelAdmin):
    """
    For modifying model representation in Admin
    """

    list_display = ("merchant", "today_val", "txn_val_l30", "txn_val_alltime")

admin.site.register(Rule)
admin.site.register(Product)
admin.site.register(ETFTransaction)
admin.site.register(Threshold)
admin.site.register(ThresholdEmails)
admin.site.register(MerchantMetric)
admin.site.register(MerchantMetricEmail)
