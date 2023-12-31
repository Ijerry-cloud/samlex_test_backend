from decimal import Decimal
from django.shortcuts import render, get_object_or_404
import io, csv, pandas as pd
from .models import File, Item, Category
from .serializers import  FileUploadSerializer, SaveFileSerializer, ItemSerializer, CategorySerializer
from rest_framework import generics, status, response
from datetime import datetime
from django.db import transaction
from accounts.permissions import *
from rest_framework.permissions import IsAuthenticated
from accounts.authentication import BearerTokenAuthentication

PARAM_QUERY_BY_ITEM_NAME = "name"
PARAM_QUERY_PAGE_NUMBER = "page"
PARAM_QUERY_BY_CATEGORY_NAME = "name"

class UploadFileView(generics.CreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ItemsAccessPermission]
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
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ItemsAccessPermission]
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        reader = pd.read_csv(file)
        read_values = reader.fillna(0)

        for _, row in read_values.iterrows():
            row_category = str(row['Category'])
            row_category = row_category.lower()

            category, category_created = Category.objects.get_or_create(name=row_category)

            item, created = Item.objects.get_or_create(name=str(row['Item Name']).strip())

            item.category = category
            item.cost_price = row['Cost Price']
            item.unit_price = Decimal(str(row['Unit Price']).replace(",", ""))
            item.quantity = row['Quantity']
            item.reorder_level = row['Reorder Level']
            item.save()


            """
            if not created:
                data = dict()
                data['employee'] = request.user.username
                data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data['quantity'] = row['Quantity']

                current_history = item.edit_history         # Get the current JSON data list
                current_history.append(data)                # Append the new JSON data
                truncated_history = current_history[-10:]   # Keep only the last ten appends
                item.edit_history = truncated_history        # Update the 'json_field' with the truncated data
                item.save()

            """


        return response.Response({"status": "success"},
                        status=status.HTTP_201_CREATED)

class ListCreateItemView(generics.CreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ItemsAccessPermission]

    def get(self, request, *args, **kwargs):
        items = Item.objects.all()

        if request.query_params.get(PARAM_QUERY_BY_ITEM_NAME):
            items = items.filter(name__icontains=request.query_params.get(PARAM_QUERY_BY_ITEM_NAME))

        if not request.query_params.get(PARAM_QUERY_PAGE_NUMBER): #dont paginate if "page" is not in query parameter
            items_serializer = ItemSerializer(items, many=True)
            return response.Response(
                items_serializer.data,
                status=status.HTTP_200_OK
            )

        items_serializer = ItemSerializer(self.paginate_queryset(items), many=True)

        return self.paginator.get_paginated_response(items_serializer.data)
    
    def post(self, request, *args, **kwargs):
        data = dict()

        if Item.objects.filter(name=request.data.get("name")):
                return response.Response({
                    "detail": "This Item already exists",
                }, status=status.HTTP_400_BAD_REQUEST)

        
        serializer = ItemSerializer(data=request.data, partial=True)
        
        if serializer.is_valid(raise_exception=False):
            
            serializer.save()
            #print(serializer.data)
            return response.Response({
                "detail": serializer.data
            }, status=status.HTTP_200_OK)
        #print(serializer.errors)
        return response.Response(
            {
                "error": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
class UpdateItemView(generics.CreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ItemsAccessPermission]
    
    def post(self, request, *args, **kwargs):
        item = get_object_or_404(Item, id=request.data.get("id"))
        #locked_instance = Item.objects.select_for_update().get(pk=item.pk) #lock that instance's rows as we are going to make multiple save and we wish to avoid race conditions

        serializer = ItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=False):

            amount_to_add = int(request.data.get('amount_to_add', 0))
            employee = request.user.username
            serializer.update(serializer.instance, serializer.validated_data, amount_to_add=amount_to_add, employee=employee)

            #locked_instance.quantity += int(request.data.get("quantity"))

            #data = dict()
            #data['employee'] = request.user.username
            #data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #data['quantity'] = request.data.get('quantity')

            #current_history = locked_instance.edit_history         # Get the current JSON data list
            #current_history =  [data] + current_history              # prepend the new JSON data
            #truncated_history = current_history[:10]   # Keep only the first ten
            #locked_instance.edit_history = truncated_history        # Update the 'json_field' with the truncated data
            #locked_instance.save()

            return response.Response({
                "detail": serializer.data
            }, status=status.HTTP_200_OK)
        #print(serializer.errors)
        return response.Response(
            {
                "error": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

class UpdateItemGroupView(generics.CreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ItemsAccessPermission]

    def post(self, request, *args, **kwargs):

        #check that items is passed the form
        if not request.data.get("items"):
            return response.Response(
            {
                "error": "missing parameter"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

        item_ids = request.data.get("items").split(",")
        items = Item.objects.filter(id__in=item_ids)

        amount_to_add = int(request.data.get('groupAdd', 0))
        employee = request.user.username

        for item in items:
            with transaction.atomic():
                if amount_to_add > 0:
                    data = dict()
                    item.quantity = item.quantity + amount_to_add
                    data['employee'] = employee
                    data['amount_added'] = amount_to_add
                    data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")                
                    edit_history = [data] + item.edit_history
                    item.edit_history = edit_history[:10]
                    
                if request.data.get("groupReorder"):
                    item.reorder_level = int(request.data.get("groupReorder"))
                
                if request.data.get("groupTax1"):
                    item.tax1_percent = int(request.data.get("groupTax1"))
                
                if request.data.get("groupTax2"):
                    item.tax2_percent = int(request.data.get("groupTax2"))

                item.save()
        return response.Response({
                "detail": "success"
            }, status=status.HTTP_200_OK)


class DeleteItemView(generics.CreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ItemsAccessPermission]

    def post(self, request, *args, **kwargs):
        item_id = request.data.get("id")

        item = get_object_or_404(Item, id=item_id)
        item.delete()

        return response.Response({'detail': 'success', 'id': item_id}, status=status.HTTP_200_OK)

class DeleteItemGroupView(generics.CreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ItemsAccessPermission]

    def post(self, request, *args, **kwargs):

        #check that items is passed the form
        if not request.data.get("items"):
            return response.Response(
            {
                "error": "missing parameter"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

        item_ids = request.data.get("items").split(",")
        items = Item.objects.filter(id__in=item_ids)

        for item in items:
            item.delete()

        return response.Response({
                "detail": "success"
            }, status=status.HTTP_200_OK)


class ListCreateCategoryView(generics.CreateAPIView):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()

        if request.query_params.get(PARAM_QUERY_BY_CATEGORY_NAME):
            categories = categories.filter(name__icontains=request.query_params.get(PARAM_QUERY_BY_CATEGORY_NAME))

        categories_serializer = CategorySerializer(categories, many=True)

        return response.Response(categories_serializer.data, status=status.HTTP_200_OK)