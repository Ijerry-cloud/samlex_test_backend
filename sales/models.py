from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from uuid import uuid4
from django.contrib.auth import get_user_model
from people.models import Customer
uuid = models.UUIDField(default=uuid4, editable=False)


User = get_user_model()

class Sale(models.Model):

    """
        instance of an Sales
    """

    REGISTER_MODE = (
        ("sales", "Sales"),
        ("return", "Return")
    )
    PAYMENT_TYPE = (
        ("cash", "Cash"),
        ("cheque", "Cheque"),
        ("gift", "Gift card"),
        ("debit", "Debit card"),
        ("credit", "Credit card")
    )

    sales_id = models.UUIDField(default=uuid4, editable=False)
    customer = models.ForeignKey(Customer, related_name='sales', null=True, blank=True, on_delete=models.SET_NULL)
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    customer_address = models.CharField(max_length=100, null=True, blank=True)
    customer_email = models.CharField(max_length=100, null=True, blank=True) #should you use EmailField since the data coming from the frontend is assumed to already be in email(what if request is sent via postman for instance)
    register_mode = models.CharField(
        max_length=50, choices=REGISTER_MODE, default="sales", null=True, blank=True
    )
    payment_type = models.CharField(
        max_length=50, choices=PAYMENT_TYPE, default="cash", null=True, blank=True
    )
    items = models.JSONField(default=list)
    paid_cash = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)
    sum_items = models.IntegerField()
    employee = models.ForeignKey(User, related_name='sales', null=True, blank=True, on_delete=models.SET_NULL)
    employee_name = models.CharField(max_length=100, null=True, blank=True)
    employee_dept = models.CharField(max_length=20, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ("-date",)
