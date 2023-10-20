from django.contrib import admin
from .models import File, Item, Category


class FileAdmin(admin.ModelAdmin):
    list_display = ["id", "staff_name", "position", "age",   "year_joined"]

class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'cost_price', 'unit_price', 'quantity', 'reorder_level', 'id']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']

admin.site.register(File, FileAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Category, CategoryAdmin)






