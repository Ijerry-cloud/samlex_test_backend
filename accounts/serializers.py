from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ['password']

    def get_department_name(self, obj):
        return obj.get_dept_display()
        
class CreateUserSerializer(serializers.ModelSerializer):
    
    
    class Meta: 
        model = User
        fields = "__all__"
        