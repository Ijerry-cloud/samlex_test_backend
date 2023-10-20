from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from accounts.authentication import BearerTokenAuthentication
from people.models import Customer
from .models import Sale
from .serializers import SaleSerializer

User = get_user_model()

class ListCreateSalesView(generics.ListCreateAPIView):
    def get(self, request, *args, **kwargs):
        sales = Sale.objects.filter(employee = request.user.id)

        sales_serializer  = SaleSerializer(self.paginate_queryset(sales), many=True)

        return self.paginator.get_paginated_response(sales_serializer.data)
    
    def post(self, request, *args, **kwargs):
        data = dict()

        try:
            customer = get_object_or_404(Customer, id=request.data.get('customerID'))
            employee = get_object_or_404(User, id=request.user.id)
            sale = Sale.objects.create(
                customer =customer,
                customer_name = request.data.get('customerName'),
                customer_email = request.data.get('customerEmail'),
                customer_address = request.data.get('customerAddress'),
                items = request.data.get('selectedOptions'), #should unit_price be determined by whatever the user sends to the backend or what is stored on the database at that point in time
                paid_cash = request.data.get('paidCash'),
                sum_items = request.data.get('sum_items'),
                sub_total = request.data.get('sub_total'),
                payment_type = request.data.get('paymentType'),
                register_mode = request.data.get('mode'),
                discount = request.data.get('discount'),
                employee = employee,
                employee_name = request.user.username,
                employee_dept = request.user.dept,
                comments = request.data.get('comments')


            )
            sale.save()

            sale = SaleSerializer(sale).data
            data = sale

            return response.Response(
                data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print(e)
            return response.Response(
                {
                    "detail": "Oops! something went wrong, please contact the admin",
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        