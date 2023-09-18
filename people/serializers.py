from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Supplier
        fields = "__all__"