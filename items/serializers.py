from rest_framework import serializers
from .models import File, Item


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
class SaveFileSerializer(serializers.Serializer):
    
    class Meta:
        model = File
        fields = "__all__"

class ItemSerializer(serializers.Serializer):

    class Meta:
        model = Item
        fields = "__all__"