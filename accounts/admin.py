from django.contrib import admin

from .models import User, StoreConfig


class UserAdmin(admin.ModelAdmin):
    """
    For moditying model representation in Admin
    """

    list_display = ("email", "first_name", "last_name", "dept")

class ConfigAdmin(admin.ModelAdmin):
    list_display = ("name", )


admin.site.register(User, UserAdmin)
admin.site.register(StoreConfig, ConfigAdmin)



