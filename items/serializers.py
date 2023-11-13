from rest_framework import serializers
from .models import File, Item, Category


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
class SaveFileSerializer(serializers.Serializer):
    
    class Meta:
        model = File
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    items = serializers.StringRelatedField(many=True)
    label =  serializers.SerializerMethodField()
    value =  serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_label(self, obj):
        return obj.name
    
    def get_value(self, obj):
        return obj.id
             

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

