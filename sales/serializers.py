from rest_framework import serializers
from .models import Sale

class SaleSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()

    class Meta: 
        model = Sale
        fields = "__all__"

    def get_customer(self, obj):
        customer = obj.customer.first_name
        if customer:
            return customer
        return None
    
    def get_employee(self, obj):
        employee = obj.employee.username
        if employee:
            return employee
        return None