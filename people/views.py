from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from accounts.authentication import BearerTokenAuthentication
from accounts.permissions import CustomerAccessPermission
from .models import Supplier
from .serializers import SupplierSerializer

User = get_user_model() #dont think this is needed

class ListCreateSupplierView(generics.ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        suppliers = Supplier.objects.all()

        suppliers_serializer = SupplierSerializer(self.paginate_queryset(suppliers), many=True)

        return self.paginator.get_paginated_response(suppliers_serializer.data)
    
    def post(self, request, *args, **kwargs):
        data = dict()

        try:
            if Supplier.objects.filter(company_name=request.data.get("company_name")):
                return response.Response({
                    "detail": "This Company name already exists",
                }, status=status.HTTP_400_BAD_REQUEST)
            
            supplier = Supplier.objects.create(
                **request.data
            )
            supplier.save()

            supplier = SupplierSerializer(supplier).data
            data['detail'] = supplier

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

class UpdateSupplierView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        supplier = get_object_or_404(Supplier, uuid=request.data.get("uuid"))

        serializer = SupplierSerializer(supplier, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=False):
            serializer.save()

            return response.Response({
                "detail": serializer.data
            }, status=status.HTTP_200_OK)
        return response.Response(
            {
                "error": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    
class DeleteSupplierView(generics.CreateAPIView):
    authentication_classes= [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        supplier = get_object_or_404(Supplier, uuid=request.data.get("uuid"))
        supplier.delete()

        return response.Response({'detail': 'success'}, status=status.HTTP_200_OK)

