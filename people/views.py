from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from accounts.authentication import BearerTokenAuthentication
from accounts.permissions import CustomerAccessPermission
from .models import Supplier, Customer
from .serializers import SupplierSerializer, CustomerSerializer
from django.db.models import Count, Q

User = get_user_model() #dont think this is needed

PARAM_QUERY_BY_SUPPLIER_NAME = "company_name"
PARAM_QUERY_PAGE_NUMBER = "page"
PARAM_QUERY_BY_CUSTOMER_NAME = "name"


class ListCreateSupplierView(generics.ListCreateAPIView):

    def get(self, request, *args, **kwargs):
        suppliers = Supplier.objects.all()
        
        if request.query_params.get(PARAM_QUERY_BY_SUPPLIER_NAME):
            suppliers = suppliers.filter(company_name__icontains=request.query_params.get(PARAM_QUERY_BY_SUPPLIER_NAME))

        if not request.query_params.get(PARAM_QUERY_PAGE_NUMBER): #dont paginate if "page" is not in query parameter
            suppliers_serializer = SupplierSerializer(suppliers, many=True)
            return response.Response(
                suppliers_serializer.data,
                status=status.HTTP_200_OK
            )

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

class ListCreateCustomerView(generics.ListCreateAPIView):
    def get(self, request, *args, **kwargs):
        customers = Customer.objects.all()

        if request.query_params.get(PARAM_QUERY_BY_CUSTOMER_NAME):
            customers = customers.filter(Q(first_name__icontains=request.query_params.get(PARAM_QUERY_BY_CUSTOMER_NAME)) | Q(last_name__icontains=request.query_params.get(PARAM_QUERY_BY_CUSTOMER_NAME)))

        if not request.query_params.get(PARAM_QUERY_PAGE_NUMBER): #dont paginate if "page" is not in query parameter
            customers_serializer = CustomerSerializer(customers, many=True)
            print(customers_serializer.data)
            return response.Response(
                customers_serializer.data,
                status=status.HTTP_200_OK
            )
        customers_serializer = CustomerSerializer(self.paginate_queryset(customers), many=True)

        return self.paginator.get_paginated_response(customers_serializer.data)

    def post(self, request, *args, **kwargs):
        data = dict()

        try:
            customer = Customer.objects.create(
                    **request.data
            )
            customer.save()

            customer = CustomerSerializer(customer).data
            data['detail'] = customer

            return response.Response(
                data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return response.Response(
                {
                    "detail": "Oops! something went wrong, please contact the admin",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class UpdateCustomerView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        customer = get_object_or_404(Customer, uuid=request.data.get("uuid"))


        serializer = CustomerSerializer(customer, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=False):
            serializer.save()

            return response.Response({
                "detail": serializer.data
            }, status=status.HTTP_200_OK)
        print(request.data)
        print(serializer.data)
        print(serializer.errors)
        return response.Response(
            {
                "error": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    

class DeleteCustomerView(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        customer = get_object_or_404(Customer, uuid=request.data.get("uuid"))
        customer.delete()

        return response.Response({'detail': 'success'}, status=status.HTTP_200_OK)


