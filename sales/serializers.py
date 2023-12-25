from rest_framework import serializers
from .models import Sale
from people.serializers import CustomerSerializer

class SaleSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()

    class Meta: 
        model = Sale
        fields = "__all__"

    def get_customer(self, obj):
        customer = obj.customer
        if customer:
            return customer.first_name
        return None
    
    def get_employee(self, obj):
        employee = obj.employee
        if employee:
            return employee.username
        return None
    

class DailyReportSerializer(serializers.ModelSerializer):
    day = serializers.DateField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    no_of_sales = serializers.IntegerField()
    total_items = serializers.IntegerField()

    class Meta:
        model = Sale
        fields = ('day', 'total_amount', 'no_of_sales', 'total_items')

class CustomerReportSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=15, decimal_places=2)
    no_of_sales = serializers.IntegerField()
    total_items = serializers.IntegerField()
    customers_name = serializers.StringRelatedField()


    class Meta:
        model = Sale
        fields = ('customers_name', 'total_amount', 'total_paid', 'no_of_sales', 'total_items')

class EmployeeReportSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=15, decimal_places=2)
    no_of_sales = serializers.IntegerField()
    total_items = serializers.IntegerField()
    employees_name = serializers.StringRelatedField()


    class Meta:
        model = Sale
        fields = ('employees_name', 'total_amount', 'total_paid', 'no_of_sales', 'total_items')

    