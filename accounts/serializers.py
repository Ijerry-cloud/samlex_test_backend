from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import StoreConfig


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    
    department_name = serializers.SerializerMethodField()
    sales = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        exclude = ['password']

    def get_department_name(self, obj):
        return obj.get_dept_display()
    

    
class GetAllUsersSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    colorScheme = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('label', 'value', 'colorScheme')

    def get_label(self, obj):
        return obj.username

    def get_value(self, obj):
        return obj.id
    
    def get_colorScheme(self, obj):
        return "none"  
        
class CreateUserSerializer(serializers.ModelSerializer):
    
    
    class Meta: 
        model = User
        fields = "__all__"

class StoreConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreConfig
        fields = "__all__"

        