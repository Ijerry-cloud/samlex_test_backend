from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Supplier, Customer


class SupplierSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Supplier
        fields = "__all__"

class CustomerSerializer(serializers.ModelSerializer):
    sales = serializers.StringRelatedField(many=True)

    class Meta: 
        model = Customer
        fields = "__all__"