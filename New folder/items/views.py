from django.shortcuts import render
import io, csv, pandas as pd
from .models import File, Item
from .serializers import  FileUploadSerializer, SaveFileSerializer
from rest_framework import generics, status, response

class UploadFileView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        reader = pd.read_csv(file)
        for _, row in reader.iterrows():
            new_file = File(
                       id = row['id'],
                       staff_name= row["Staff Name"],
                       position= row['Designated Position'],
                       age= row["Age"],
                       year_joined= row["Year Joined"]
                       )
            new_file.save()
        return response.Response({"status": "success"},
                        status=status.HTTP_201_CREATED)
    
class UploadItemCSVFileView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        reader = pd.read_csv(file)
        read_values = reader.fillna(0)
        print(read_values)

        for _, row in read_values.iterrows():
            new_item = Item(
                name = row['Item Name'],
                category = row['Category'],
                cost_price = row['Cost Price'],
                unit_price = row['Unit Price'],
                quantity = row['Quantity'],
                reorder_level = row['Reorder Level']
            ) 
            new_item.save()
        return response.Response({"status": "success"},
                        status=status.HTTP_201_CREATED)
