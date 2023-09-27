from django.db import models
from uuid import uuid4

class Supplier(models.Model):
    """
        instance of a supplier
    """
    uuid = models.UUIDField(default=uuid4, editable=False)
    company_name = models.CharField(unique=True, max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_no = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address_1 = models.CharField(max_length=100, null=True, blank=True)
    address_2 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=20, null=True, blank=True)
    zip = models.CharField(max_length=15, null=True, blank=True)
    country = models.CharField(max_length=20, null=True, blank=True)
    comments = models.TextField(max_length=20, null=True, blank=True)
    account = models.CharField(max_length=100, null=True, blank=True) 

    class Meta:
        ordering = ("company_name",)