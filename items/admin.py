

from django.contrib import admin
from .models import File, Item


class FileAdmin(admin.ModelAdmin):
    list_display = ["id", "staff_name", "position", "age",   "year_joined"]



class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'cost_price', 'unit_price', 'quantity', 'reorder_level']

admin.site.register(File, FileAdmin)
admin.site.register(Item, ItemAdmin)



