from django.contrib import admin

from .models import Supplier


class SupplierAdmin(admin.ModelAdmin):
    """
    For moditying model representation in Admin
    """

    list_display = ("company_name", "first_name", "last_name")


admin.site.register(Supplier, SupplierAdmin)
