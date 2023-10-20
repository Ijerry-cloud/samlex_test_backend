from django.contrib import admin
from .models import Sale

class SaleAdmin(admin.ModelAdmin):
    list_display = ['sales_id', 'customer', 'payment_type', 'items', 'discount', 'employee', 'date']

admin.site.register(Sale, SaleAdmin)