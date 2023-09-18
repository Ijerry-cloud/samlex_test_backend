from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .query import BulkUpdateOrCreateQuerySet

class Bank(models.Model):
    """
    Instance of Bank
    """

    name = models.CharField(max_length=50, blank=True, default="")
    code = models.CharField(max_length=50, unique=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name


class Merchant(models.Model):
    """
    Instance of Merchant
    """

    mid = models.CharField(_("merchant ID"), max_length=50, null=True)
    name = models.CharField(max_length=50, blank=True, default="")
    band = models.CharField(max_length=50, blank=True, default="")
    terminal_count = models.IntegerField(null=True, blank=True)
    top_customer = models.CharField(max_length=50, blank=True, default="")
    updated = models.DateTimeField(auto_now=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    def __str__(self) -> str:
        return self.mid


class Terminal(models.Model):
    """
    Instance of Terminal
    """

    tid = models.CharField(_("Terminal ID"), max_length=50, unique=True)
    sn = models.CharField(_("serial no"), max_length=50, blank=True, default="")
    cs = models.CharField(
        _("last hour charging status"), max_length=50, blank=True, default=""
    )
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    def __str__(self) -> str:
        return self.tid


class Customer(models.Model):
    """
    Instance of POS Customer
    """

    pan = models.CharField(_("Card PAN"), max_length=50)
    card_issuer = models.ForeignKey(Bank, on_delete=models.CASCADE)
    card_expiry = models.CharField(max_length=50, blank=True, default="")
    last_txn_value = models.DecimalField(
        _("Txn Value Last 30 days"),
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )
    last_txn_status = models.CharField(max_length=50, blank=True, default="")
    last_txn_date = models.DateTimeField(null=True, blank=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    def __str__(self) -> str:
        return self.pan


class BankSummary(models.Model):
    """
    Instance of Bank Summary
    """

    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    txn_vol_l30 = models.IntegerField(
        _("Txn Volume Last 30 days"), null=True, blank=True
    )
    txn_val_l30 = models.DecimalField(
        _("Txn Value Last 30 days"),
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )
    txn_vol_success_l30 = models.IntegerField(
        _("Successful Txn Volume Last 30 days"), null=True, blank=True
    )
    txn_val_success_l30 = models.DecimalField(
        _("Successful Txn Value Last 30 days"),
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )
    txn_vol_failed_l30 = models.IntegerField(
        _("Failed Txn Volume Last 30 days"), null=True, blank=True
    )
    txn_val_failed_l30 = models.DecimalField(
        _("Failed Txn Value Last 30 days"),
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )
    txn_vol_alltime = models.IntegerField(
        _("Txn Volume All Time"), null=True, blank=True
    )
    txn_val_alltime = models.DecimalField(
        _("Txn Value All Time"), max_digits=20, decimal_places=2, null=True, blank=True
    )
    txn_vol_success_alltime = models.IntegerField(
        _("Successful Txn Volume All Time"), null=True, blank=True
    )
    txn_val_success_alltime = models.DecimalField(
        _("Successful Txn Value All Time"),
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )
    txn_vol_failed_alltime = models.IntegerField(
        _("Failed Txn Volume All Time"), null=True, blank=True
    )
    txn_val_failed_alltime = models.DecimalField(
        _("Failed Txn Value All Time"),
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )
    today_vol_success = models.IntegerField(
        _("Today Volume Success"), null=True, blank=True
    )
    today_val_success = models.DecimalField(
        _("Today Value Success"), max_digits=20, decimal_places=2, null=True, blank=True
    )
    today_vol_failed = models.IntegerField(
        _("Today Volume Failed"), null=True, blank=True
    )
    today_val_failed = models.DecimalField(
        _("Today Value Failed"), max_digits=20, decimal_places=2, null=True, blank=True
    )
    today_vol = models.IntegerField(_("Today Volume"), null=True, blank=True)
    today_val = models.DecimalField(
        _("Today Value"), max_digits=20, decimal_places=2, null=True, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        """
        Model Meta
        """

        verbose_name_plural = "Banks' Summaries"
        ordering = ("-created",)

    def __str__(self) -> str:
        return self.bank.name


class MerchantSummary(models.Model):
    """
    Instance of Merchant Summary
    """

    merchant = models.ForeignKey(Merchant, on_delete=models.SET_NULL, null=True)
    txn_vol_l30 = models.IntegerField(
        _("Txn Volume Last 30 days"), null=True, blank=True
    )
    txn_val_l30 = models.DecimalField(
        _("Txn Value Last 30 days"),
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )
    txn_vol_success_l30 = models.IntegerField(
        _("Txn Volume Successful Last 30 days"), null=True, blank=True
    )
    txn_val_success_l30 = models.DecimalField(
        _("Txn Value Successful Last 30 days"),
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )
    txn_vol_failed_l30 = models.IntegerField(
        _("Txn Volume Failed Last 30 days"), null=True, blank=True
    )
    txn_val_failed_l30 = models.DecimalField(
        _("Txn Value Failed Last 30 days"),
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )
    txn_vol_alltime = models.IntegerField(
        _("Txn Volume All Time"), null=True, blank=True
    )
    txn_val_alltime = models.DecimalField(
        _("Txn Value All Time"), max_digits=20, decimal_places=2, null=True, blank=True
    )
    txn_vol_success_alltime = models.IntegerField(
        _("Successful Txn Volume All Time"), null=True, blank=True
    )
    txn_val_success_alltime = models.DecimalField(
        _("Successful Txn Value All Time"),
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )
    txn_vol_failed_alltime = models.IntegerField(
        _("Failed Txn Volume All Time"), null=True, blank=True
    )
    txn_val_failed_alltime = models.DecimalField(
        _("Failed Txn Value All Time"),
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
    )
    today_vol_success = models.IntegerField(
        _("Today Volume Success"), null=True, blank=True
    )
    today_val_success = models.IntegerField(
        _("Today Value Success"), null=True, blank=True
    )
    today_vol_failed = models.IntegerField(
        _("Today Volume Failed"), null=True, blank=True
    )
    today_val_failed = models.IntegerField(
        _("Today Value Failed"), null=True, blank=True
    )
    today_vol = models.IntegerField(_("Today Volume"), null=True, blank=True)
    today_val = models.IntegerField(_("Today Value"), null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        """
        Model Meta
        """

        verbose_name_plural = "Merchants' Summaries"
        ordering = ("-created",)

    def __str__(self) -> str:
        return self.merchant.mid


class Product(models.Model):

    product_name = models.CharField(max_length=50, null=True, blank=True, unique=True)
    product_type = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Rule(models.Model):

    description = models.CharField(max_length=1000, null=True, blank=True)
    product_type = models.CharField(max_length=1000, null=True, blank=True)
    condition = models.CharField(max_length=1000, null=True, blank=True)
    active = models.BooleanField(default=True, null=True)
    # value = models.IntegerField(_("value"), null=True, blank=True)
    value = models.CharField(max_length=1000, null=True, blank=True)
    value2 = models.CharField(max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(
        get_user_model(),
        related_name='rule_created_by',
        null=True,
        on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        get_user_model(),
        related_name='rule_last_updated_by',
        null=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.description


class Threshold(models.Model):

    rule = models.ForeignKey(Rule, null=True, on_delete=models.CASCADE)
    value = models.IntegerField(_("value"), null=True, blank=True)
    level = models.CharField(max_length=255, null=True, blank=True) # choices, "manageable", "warning", "danger"
    created_by = models.ForeignKey(
        get_user_model(),
        related_name='threshold_created_by',
        null=True,
        on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        get_user_model(),
        related_name='threshold_last_updated_by',
        null=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class ThresholdEmails(models.Model):

    threshold = models.ForeignKey(Threshold, null=True, on_delete=models.CASCADE)
    level = models.CharField(max_length=255, null=True, blank=True) # choices, "manageable", "warning", "danger"
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)


class LogTable(models.Model):

    error_message = models.TextField(null=True, blank=True)
    timestamps = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'log_table'


class EmailLogTable(models.Model):

    rule = models.ForeignKey(Rule, null=True, on_delete=models.SET_NULL)
    threshold = models.ForeignKey(Threshold, null=True, on_delete=models.SET_NULL)
    recipients = models.CharField(max_length=1000, blank=True, null=True)
    message = models.CharField(max_length=1000, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class ETFTransaction(models.Model):

    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True,blank=True)
    transaction_type = models.CharField(max_length=100, null=True, blank=True)
    account = models.CharField(max_length=50, null=True, blank=True)
    account_type = models.CharField(max_length=50, null=True, blank=True)
    wallet_id = models.CharField(max_length=50, null=True, blank=True)
    channel = models.CharField(max_length=50, null=True, blank=True)
    reference = models.CharField(max_length=50, null=True, blank=True)
    transaction_status = models.CharField(max_length=50, null=True, blank=True)
    reversal = models.BooleanField(default=False, null=True, blank=True)
    credit_status = models.BooleanField(default=False, null=True, blank=True)
    user_id = models.CharField(max_length=50, null=True, blank=True)
    mongo_id = models.CharField(max_length=50, unique=True, null=True, blank=True) # use the mongo db id to ensure uniqueness of transaction
    unique_id = models.CharField(max_length=80, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    provider_reference = models.CharField(max_length=100, null=True, blank=True)
    provider = models.CharField(max_length=100, null=True, blank=True)
    product = models.CharField(max_length=100, null=True, blank=True)
    
    debit_response = models.JSONField(default=dict, null=True, blank=True)
    response = models.JSONField(default=dict, null=True, blank=True)
    monitoring_status = models.CharField(max_length=100, null=True, blank=True)
    monitoring_comments = models.CharField(max_length=1000, null=True, blank=True)
    
    transaction_created_at = models.DateTimeField(null=True, blank=True)
    transaction_updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ETFUser(models.Model):

    mongo_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    data = models.JSONField(default=dict, null=True, blank=True)

    def get_name(self):
        if self.data.get("businessName"):
            return self.data.get("businessName")
        if self.data.get("username"):
            return self.data.get("username")
        if self.data.get("firstName"):
            return "%s %s" % (self.data.get("firstName"), self.data.get("lastName"))
        

class MerchantMetric (models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)
    no_of_days = models.IntegerField(null=True, blank=True)
    minimum_amount = models.IntegerField(null=True, blank=True, default=0)
    sending_intervals = models.IntegerField(null=True, blank=True, default=0)  # sending intervals in hours, determines how often this mail is sent
    percentage_violation = models.IntegerField(null=True, blank=True)


class MerchantMetricEmail (models.Model):

    merchant_metric = models.ForeignKey(MerchantMetric, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)


class MerchantMetricEmailLog(models.Model):

    description = models.CharField(max_length=3000, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
