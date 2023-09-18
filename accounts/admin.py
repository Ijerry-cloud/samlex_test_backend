from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    """
    For moditying model representation in Admin
    """

    list_display = ("email", "first_name", "last_name", "dept")


admin.site.register(User, UserAdmin)
