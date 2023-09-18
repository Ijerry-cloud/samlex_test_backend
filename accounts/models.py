from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default User model
    """

    USER_DEPTS = (
        ("tech", "Technology"),
        ("ICT", "ICT"),
        ("sales", "Sales management"),
        ("admin", "Administration"),
    )

    USER_GENDER = (
        ("male", "Male"),
        ("female", "Female")
    )

    username = models.CharField(
        max_length=50,
        unique=True,
        error_messages={
            "unique": "A user with that username address already exists.",
        },
    )
    uuid = models.UUIDField(default=uuid4, editable=False)
    email_confirmed = models.BooleanField(default=False)
    is_lead = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_no = models.CharField(max_length=15, null=True, blank=True)
    address_1 = models.CharField(max_length=100, null=True, blank=True)
    address_2 = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=20, null=True, blank=True)
    zip = models.CharField(max_length=15, null=True, blank=True)
    country = models.CharField(max_length=20, null=True, blank=True)
    customer_perm = models.BooleanField(default=False)
    items_perm = models.BooleanField(default=False)
    item_kits_perm = models.BooleanField(default=False)
    suppliers_perm = models.BooleanField(default=False)
    reports_perm = models.BooleanField(default=False)
    receivings_perm = models.BooleanField(default=False)
    sales_perm = models.BooleanField(default=False)
    employees_perm = models.BooleanField(default=False)
    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "A user with that email address already exists.",
        },
    )
    dept = models.CharField(
        _("user dept"), max_length=50, choices=USER_DEPTS, default="tech", null=True
    )
    gender = models.CharField(
        max_length=50, choices=USER_GENDER, default="male", null=True
    )

    objects = UserManager()

    # Set email as username field and remove username from required fields
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ("-date_joined",)
        get_latest_by = ("-date_joined",)

    def __str__(self):
        return self.email
