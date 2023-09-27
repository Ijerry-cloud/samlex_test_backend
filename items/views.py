from decimal import Decimal
from django.shortcuts import render
import io, csv, pandas as pd
from .models import File, Item
from .serializers import  FileUploadSerializer, SaveFileSerializer, ItemSerializer
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

        category = []

        for _, row in read_values.iterrows():
            if str(row['Category']).lower() not in category:
                category.append(str(row['Category']).lower())
            new_item = Item(
                name = row['Item Name'],
                category = row['Category'],
                cost_price = row['Cost Price'],
                unit_price = Decimal(str(row['Unit Price']).replace(",", "")), #first convert value to string
                                                                                #(to be sure every value is a string
                                                                                # so that replace method can be used )
                                                                                # then convert to decimal
                
                quantity = row['Quantity'],
                reorder_level = row['Reorder Level']
            ) 
            new_item.save()
        print(category, len(category))
        return response.Response({"status": "success"},
                        status=status.HTTP_201_CREATED)

class ListCreateItemView(generics.CreateAPIView):

    def get(self, request, *args, **kwargs):
        items = Item.objects.all()

        items_serializer = ItemSerializer(self.paginate_queryset(items), many=True)

        return self.paginator.get_paginated_response(items_serializer.data)
    
    def post(self, request, *args, **kwargs):
        data = dict()

        try:
            if Item.objects.filter(name=request.data.get("name")):
                return response.Response({
                    "detail": "This Item already exists",
                }, status=status.HTTP_400_BAD_REQUEST)
            
            item = Item.objects.create(
                **request.data
            )
            item.save()

            item = ItemSerializer(item).data
            data['detail'] = item

            return response.Response(
                data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            #print(e)
            return response.Response(
                {
                    "detail": "Oops! something went wrong, please contact the admin",
                },
                status=status.HTTP_400_BAD_REQUEST
            )