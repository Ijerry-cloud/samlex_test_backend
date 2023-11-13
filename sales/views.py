from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, response
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from accounts.authentication import BearerTokenAuthentication
from people.models import Customer
from .models import Sale
from items.models import Item
from items.serializers import ItemSerializer
from .serializers import SaleSerializer, DailyReportSerializer, CustomerReportSerializer, EmployeeReportSerializer
from datetime import datetime, time
from django.db.models import Q, Count, Sum, F, Value, CharField
from django.db.models.functions import Concat
import json
from django.db.models.functions import TruncDate
from utilities.utilities import start_end_datetime

User = get_user_model()


class ListCreateSalesView(generics.ListCreateAPIView):
    def get(self, request, *args, **kwargs):
        sales = Sale.objects.filter(employee=request.user.id)

        sales_serializer = SaleSerializer(
            self.paginate_queryset(sales), many=True)

        return self.paginator.get_paginated_response(sales_serializer.data)

    def post(self, request, *args, **kwargs):
        data = dict()

        try:
            customer = get_object_or_404(
                Customer, id=request.data.get('customerID'))
            employee = get_object_or_404(User, id=request.user.id)
            sale = Sale.objects.create(
                customer=customer,
                customer_name=request.data.get('customerName'),
                customer_email=request.data.get('customerEmail'),
                customer_address=request.data.get('customerAddress'),
                # should unit_price be determined by whatever the user sends to the backend or what is stored on the database at that point in time
                items=request.data.get('selectedOptions'),
                paid_cash=request.data.get('paidCash'),
                sum_items=request.data.get('sum_items'),
                sub_total=request.data.get('sub_total'),
                payment_type=request.data.get('paymentType'),
                register_mode=request.data.get('mode'),
                discount=request.data.get('discount'),
                employee=employee,
                employee_name=request.user.username,
                employee_dept=request.user.dept,
                comments=request.data.get('comments')


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


class ListAnySalesView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get("startDate")
        end_date = request.query_params.get("endDate")
        start_date, end_date = start_end_datetime(start_date, end_date)

        sales = Sale.objects.filter(date__range=[start_date, end_date])

        if request.query_params.get("employeeIds"):
            employee_ids = request.query_params.get("employeeIds").split(",")
            sales = sales.filter(employee__in=employee_ids)

        if request.query_params.get("customerIds"):
            customer_ids = request.query_params.get("customerIds").split(",")
            sales = sales.filter(customer__in=customer_ids)

        if request.query_params.get("itemNames"):
            items = request.query_params.get("itemNames").split(",")

            key_to_match = 'name'
            filter_query = Q()

            for item in items:
                filter_query |= Q(items__contains=[{key_to_match: item}])
                print(filter_query)

            sales = sales.filter(filter_query)

        sales_serializer = SaleSerializer(
            self.paginate_queryset(sales), many=True)

        return self.paginator.get_paginated_response(sales_serializer.data)


class DeleteSalesView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        sale = get_object_or_404(Sale, id=request.data.get(
            "id"), employee=request.user.id)
        sale.delete()

        return response.Response({'detail': 'success'}, status=status.HTTP_200_OK)


class DeleteAnySaleView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        sale = get_object_or_404(Sale, id=request.data.get("id"))
        sale.delete()

        return response.Response({'detail': 'success'}, status=status.HTTP_200_OK)


class DailyReportView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get("startDate")
        end_date = request.query_params.get("endDate")
        start_date, end_date = start_end_datetime(start_date, end_date)

        sales = Sale.objects.filter(date__range=[start_date, end_date])

        days = sales.annotate(day=TruncDate('date')).values('day').annotate(total_amount=Sum(
            'sub_total'), no_of_sales=Count('id'), total_items=Sum('sum_items')).order_by('day')
        days_serializer = DailyReportSerializer(
            self.paginate_queryset(days), many=True)

        return self.paginator.get_paginated_response(days_serializer.data)


class CustomerSummaryReportView(generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get("startDate")
        end_date = request.query_params.get("endDate")
        start_date, end_date = start_end_datetime(start_date, end_date)

        sales = Sale.objects.filter(date__range=[start_date, end_date])

        if request.query_params.get("customerIds"):
            customer_ids = request.query_params.get("customerIds").split(",")
            sales = sales.filter(customer__in=customer_ids)

        customers = sales.values('customer').annotate(total_amount=Sum('sub_total'), no_of_sales=Count('id'),
                                                      total_paid=Sum('paid_cash'),
                                                      total_items=Sum('sum_items'), customers_name=Concat(F('customer__first_name'), Value(' '), F('customer__last_name'), output_field=CharField())).values('customer',
                                                                                                                                                                                                      'total_amount',
                                                                                                                                                                                                      'total_paid',
                                                                                                                                                                                                      'no_of_sales',
                                                                                                                                                                                                      'total_items',
                                                                                                                                                                                                      'customers_name').order_by('-total_paid')
        print('printing customers')
        print(customers)
        customer_report_serializer = CustomerReportSerializer(self.paginate_queryset(customers), many=True)

        return self.paginator.get_paginated_response(customer_report_serializer.data)


class EmployeeSummaryReportView(generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get("startDate")
        end_date = request.query_params.get("endDate")
        start_date, end_date = start_end_datetime(start_date, end_date)

        sales = Sale.objects.filter(date__range=[start_date, end_date])

        if request.query_params.get("employeeIds"):
            employee_ids = request.query_params.get("employeeIds").split(",")
            sales = sales.filter(employee__in=employee_ids)

        employees = sales.values('employee').annotate(total_amount=Sum('sub_total'), no_of_sales=Count('id'),
                                                      total_paid=Sum('paid_cash'),
                                                      total_items=Sum('sum_items'), employees_name=Concat(F('employee__first_name'), Value(' '), F('employee__last_name'), output_field=CharField())).values('employee',
                                                                                                                                                                                                      'total_amount',
                                                                                                                                                                                                      'total_paid',
                                                                                                                                                                                                      'no_of_sales',
                                                                                                                                                                                                      'total_items',
                                                                                                                                                                                                      'employees_name')
        employee_report_serializer = EmployeeReportSerializer(self.paginate_queryset(employees), many=True)

        return self.paginator.get_paginated_response(employee_report_serializer.data)


class ItemInventoryView(generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        items = Item.objects.all()

        if request.query_params.get("itemIds"):
            item_ids = request.query_params.get("itemIds").split(",")
            items = items.filter(id__in=item_ids)

        if request.query_params.get("min"):
            min = request.query_params.get("min")
            items = items.filter(quantity__gte=min) 

        if request.query_params.get("max"):
            max = request.query_params.get("max")
            items = items.filter(quantity__lte=max)

        items_serializer =  ItemSerializer(self.paginate_queryset(items), many=True)

        return self.paginator.get_paginated_response(items_serializer.data)

