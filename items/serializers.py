from rest_framework import serializers
from .models import File, Item, Category
from django.db import transaction
from datetime import datetime

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class SaveFileSerializer(serializers.Serializer):

    class Meta:
        model = File
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    items = serializers.StringRelatedField(many=True)
    label = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_label(self, obj):
        return obj.name

    def get_value(self, obj):
        return obj.id


class CategoryChartSerializer(serializers.ModelSerializer):

    # for the DashboardCategoryChartView in sales app
    total_quantity = serializers.IntegerField()

    class Meta:
        model = Category
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    category_data = serializers.SerializerMethodField()
    supplier_data = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    number = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    colorScheme = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = "__all__"

    def update(self, instance, validated_data, amount_to_add=None, employee=None):

        with transaction.atomic():

            if amount_to_add > 0: #perform increment and logging if amount_to_add is greater than zero
                data = dict()

                validated_data['quantity'] = instance.quantity + amount_to_add

                data['employee'] = employee
                data['amount_added'] = amount_to_add
                data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")                
                edit_history = [data] + instance.edit_history
                validated_data['edit_history'] = edit_history[:10]


            # Call the original update method to perform the standard update operation
            return super().update(instance, validated_data)

    def get_category_data(self, obj):
        category = obj.category
        if category:
            return {
                'label': category.name,
                'value': category.id,
            }
        return None

    def get_supplier_data(self, obj):
        supplier = obj.supplier
        if supplier:
            return {
                'label': supplier.company_name,
                'value': supplier.id,
            }
        return None

    def get_label(self, obj):
        return obj.name

    def get_number(self, obj):
        return 1

    def get_value(self, obj):
        return obj.name

    def get_colorScheme(self, obj):
        return "none"

