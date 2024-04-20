from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, response
from django.contrib.auth import get_user_model
from accounts.models import StoreConfig
from people.models import Customer
from .models import Sale
from items.models import Item, Category
from items.serializers import ItemSerializer, CategoryChartSerializer
from .serializers import SaleSerializer, DailyReportSerializer, CustomerReportSerializer, EmployeeReportSerializer
from datetime import datetime, time
from django.db.models import Q, Count, Sum, F, Value, CharField, Case, When, IntegerField
from django.db.models.functions import Concat
import json
from django.db.models.functions import TruncDate
from utilities.utilities import start_end_datetime
from accounts.permissions import *
from rest_framework.permissions import IsAuthenticated
from accounts.authentication import BearerTokenAuthentication
from django.db import transaction
import csv
from django.http import HttpResponse

COMPANY_NAME = "chuksdigitals"

User = get_user_model()


class ListCreateSalesView(generics.ListCreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, SalesAccessPermission]

    def get(self, request, *args, **kwargs):
        sales = Sale.objects.filter(employee=request.user.id)

        sales_serializer = SaleSerializer(
            self.paginate_queryset(sales), many=True)

        return self.paginator.get_paginated_response(sales_serializer.data)

    def post(self, request, *args, **kwargs):

        try:

            customer = get_object_or_404(
                Customer, id=request.data.get('customerID'))
            employee = get_object_or_404(User, id=request.user.id)
            config = get_object_or_404(StoreConfig, name=COMPANY_NAME)

            items_to_sell = request.data.get('selectedOptions')
            # print(1111111111)

            with transaction.atomic():

                for item_to_sell in items_to_sell:
                    # print(2222222)
                    item = get_object_or_404(Item, id=item_to_sell['id'])
                    # print(33333333)
                    # print(item_to_sell['number'])
                    item.quantity = item.quantity - int(item_to_sell['number'])

                    # print('somehow success')
                    item.save()
                    # print('success shaa')
                # print(request.data)
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
                    comments=config.sales_comments,
                    company_address=config.address,
                    company_phone1=config.phone1,
                    company_phone2=config.phone2,
                    company_email=config.email)

                if request.data.get('comments'):
                    sale.comments = request.data.get('comments')
                sale.save()

            sale = SaleSerializer(sale).data

            return response.Response(
                {'data': sale, 'print': config.print_receipt},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return response.Response(
                {
                    "detail": "Oops! something went wrong, please contact the admin",
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ListAnySalesView(generics.ListAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ReportsAccessPermission]

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
                # print(filter_query)

            sales = sales.filter(filter_query)

        if request.query_params.get("csv"):
            csv_mode = request.query_params.get("csv")
            if csv_mode.lower() == "true":

                sales_serializer = SaleSerializer(sales, many=True)

                response = HttpResponse(
                    content_type="text/csv",
                    headers={
                        "Content-Disposition": 'attachment; filename="SalesReport.csv"'},
                )
                writer = csv.writer(response)
                writer.writerow(["DATE", "EMPLOYEE", "SOLD TO",
                                "QTY", "SUBTOTAL", "DISC.", "PAID"])

                for row in sales_serializer.data:
                    writer.writerow([row['date'], row['employee_name'], row['customer_name'],
                                    row['sum_items'], row['sub_total'], row['discount'], row['paid_cash']])
                return response

        sales_serializer = SaleSerializer(
            self.paginate_queryset(sales), many=True)

        return self.paginator.get_paginated_response(sales_serializer.data)


class DeleteSalesView(generics.CreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, SalesAccessPermission]

    def post(self, request, *args, **kwargs):
        sale = get_object_or_404(Sale, id=request.data.get(
            "id"), employee=request.user.id)
        sales_id = sale.id
        sale.delete()

        return response.Response({'detail': 'success', 'id': sales_id}, status=status.HTTP_200_OK)


class DeleteAnySaleView(generics.CreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ReportsAccessPermission]

    def post(self, request, *args, **kwargs):
        sale = get_object_or_404(Sale, id=request.data.get("id"))
        sales_id = sale.id
        sale.delete()

        return response.Response({'detail': 'success', 'id': sales_id}, status=status.HTTP_200_OK)


class DailyReportView(generics.ListAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ReportsAccessPermission]

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get("startDate")
        end_date = request.query_params.get("endDate")
        start_date, end_date = start_end_datetime(start_date, end_date)

        sales = Sale.objects.filter(
            date__range=[start_date, end_date]).order_by('date')

        days = sales.annotate(day=TruncDate('date')).values('day').annotate(total_amount=Sum(
            'sub_total'), no_of_sales=Count('id'), total_items=Sum('sum_items')).order_by('day')

        if request.query_params.get("csv"):
            csv_mode = request.query_params.get("csv")
            if csv_mode.lower() == "true":
                response = HttpResponse(
                    content_type="text/csv",
                    headers={
                        "Content-Disposition": 'attachment; filename="DailySummary.csv"'},
                )
                writer = csv.writer(response)
                writer.writerow(
                    ["DATE", "NO. OF SALES	", "TOTAL QTY. SOLD", "TOTAL AMOUNT"])

                for row in days:
                    # print(row['day'].strftime("%Y-%m-%d"))
                    writer.writerow(
                        [row['day'], row['no_of_sales'], row['total_items'], row['total_amount']])
                return response

        if request.query_params.get("recent"):
            recent = int(request.query_params.get("recent"))
            days = days[:recent]

        days_serializer = DailyReportSerializer(
            self.paginate_queryset(days), many=True)

        # print(days_serializer.data)

        return self.paginator.get_paginated_response(days_serializer.data)


class CustomerSummaryReportView(generics.ListAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ReportsAccessPermission]

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get("startDate")
        end_date = request.query_params.get("endDate")
        start_date, end_date = start_end_datetime(start_date, end_date)

        sales = Sale.objects.filter(date__range=[start_date, end_date])

        if request.query_params.get("customerIds"):
            customer_ids = request.query_params.get("customerIds").split(",")
            sales = sales.filter(customer__in=customer_ids)

        customers = sales.values('customer').annotate(total_amount=Sum('sub_total'), no_of_sales=Count('id'),
                                                      total_paid=Sum(
                                                          'paid_cash'),
                                                      total_items=Sum('sum_items'), customers_name=Concat(F('customer__first_name'), Value(' '), F('customer__last_name'), output_field=CharField())).values('customer',
                                                                                                                                                                                                             'total_amount',
                                                                                                                                                                                                             'total_paid',
                                                                                                                                                                                                             'no_of_sales',
                                                                                                                                                                                                             'total_items',
                                                                                                                                                                                                             'customers_name').order_by('-total_amount')
        if request.query_params.get("csv").lower() == "true":
            response = HttpResponse(
                content_type="text/csv",
                headers={
                    "Content-Disposition": 'attachment; filename="CustomerSummary.csv"'},
            )
            writer = csv.writer(response)
            writer.writerow(["CUSTOMER NAME", "NO. OF PURCHASES	",
                            "TOTAL QTY. PURCHASED", "TOTAL AMOUNT", "TOTAL PAID"])

            for row in customers:
                writer.writerow([row['customers_name'], row['no_of_sales'],
                                row['total_items'], row['total_amount'], row['total_paid']])
            return response

        customer_report_serializer = CustomerReportSerializer(
            self.paginate_queryset(customers), many=True)

        return self.paginator.get_paginated_response(customer_report_serializer.data)


class EmployeeSummaryReportView(generics.ListAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ReportsAccessPermission]

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get("startDate")
        end_date = request.query_params.get("endDate")
        start_date, end_date = start_end_datetime(start_date, end_date)

        sales = Sale.objects.filter(date__range=[start_date, end_date])

        if request.query_params.get("employeeIds"):
            employee_ids = request.query_params.get("employeeIds").split(",")
            sales = sales.filter(employee__in=employee_ids)

        employees = sales.values('employee').annotate(total_amount=Sum('sub_total'), no_of_sales=Count('id'),
                                                      total_paid=Sum(
                                                          'paid_cash'),
                                                      total_items=Sum('sum_items'), employees_name=Concat(F('employee__first_name'), Value(' '), F('employee__last_name'), output_field=CharField())).values('employee',
                                                                                                                                                                                                             'total_amount',
                                                                                                                                                                                                             'total_paid',
                                                                                                                                                                                                             'no_of_sales',
                                                                                                                                                                                                             'total_items',
                                                                                                                                                                                                             'employees_name')
        if request.query_params.get("csv").lower() == "true":
            response = HttpResponse(
                content_type="text/csv",
                headers={
                    "Content-Disposition": 'attachment; filename="EmployeeSummary.csv"'},
            )
            writer = csv.writer(response)
            writer.writerow(["EMPLOYEE NAME", "NO. OF SALES	",
                            "TOTAL QTY. SOLD", "TOTAL AMOUNT", "TOTAL PAID"])

            for row in employees:
                writer.writerow([row['employees_name'], row['no_of_sales'],
                                row['total_items'], row['total_amount'], row['total_paid']])
            return response

        employee_report_serializer = EmployeeReportSerializer(
            self.paginate_queryset(employees), many=True)

        return self.paginator.get_paginated_response(employee_report_serializer.data)


class ItemInventoryView(generics.ListAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, ReportsAccessPermission]

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

        if request.query_params.get("csv").lower() == "true":

            items_serializer = ItemSerializer(items, many=True)

            response = HttpResponse(
                content_type="text/csv",
                headers={
                    "Content-Disposition": 'attachment; filename="ItemInventoryReport.csv"'},
            )
            writer = csv.writer(response)
            writer.writerow(["ITEM NAME", "TOTAL QTY. LEFT"])

            for row in items_serializer.data:
                writer.writerow([row['name'], row['quantity']])
            return response

        items_serializer = ItemSerializer(
            self.paginate_queryset(items), many=True)

        return self.paginator.get_paginated_response(items_serializer.data)


class DashboardGetCountView(generics.ListAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, IsSamlexAdmin]

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get("startDate")
        end_date = request.query_params.get("endDate")
        start_date, end_date = start_end_datetime(start_date, end_date)

        sales = Sale.objects.filter(date__range=[start_date, end_date])

        customers = sales.values('customer').annotate(total_amount=Sum('sub_total'), no_of_sales=Count('id'),
                                                      total_paid=Sum(
                                                          'paid_cash'),
                                                      total_items=Sum('sum_items'), customers_name=Concat(F('customer__first_name'), Value(' '), F('customer__last_name'), output_field=CharField())).values('customer',
                                                                                                                                                                                                             'total_amount',
                                                                                                                                                                                                             'total_paid',
                                                                                                                                                                                                             'no_of_sales',
                                                                                                                                                                                                             'total_items',
                                                                                                                                                                                                             'customers_name').order_by('-total_amount')

        highest_customer = customers.first()
        highest_customer_serializer = CustomerReportSerializer(
            highest_customer)

        employees = sales.values('employee').annotate(total_amount=Sum('sub_total'), no_of_sales=Count('id'),
                                                      total_paid=Sum(
                                                          'paid_cash'),
                                                      total_items=Sum('sum_items'), employees_name=Concat(F('employee__first_name'), Value(' '), F('employee__last_name'), output_field=CharField())).values('employee',
                                                                                                                                                                                                             'total_amount',
                                                                                                                                                                                                             'total_paid',
                                                                                                                                                                                                             'no_of_sales',
                                                                                                                                                                                                             'total_items',
                                                                                                                                                                                                             'employees_name').order_by('-total_amount')

        highest_employee = employees.first()
        highest_employee_serializer = EmployeeReportSerializer(
            highest_employee)

        highest_sale = sales.order_by('-sub_total').first()
        highest_sale_serializer = SaleSerializer(highest_sale)

        items_less_than_one = Item.objects.filter(quantity__lte=0).count()
        items_greater_than_ten = Item.objects.filter(quantity__gte=10).count()
        customers_without_purchase = Customer.objects.filter(
            sales__isnull=True).count()
        employees_without_sale = User.objects.filter(
            sales__isnull=True, sales_perm=True).count()

        data = dict()
        data['items'] = Item.objects.filter(quantity__gte=0).aggregate(total_sum=Sum('quantity'))['total_sum']
        data['customers'] = Customer.objects.count()
        data['sales'] = Sale.objects.count()
        data['employees'] = User.objects.count()
        data['highest_customer'] = highest_customer_serializer.data
        data['highest_employee'] = highest_employee_serializer.data
        data['highest_sale'] = highest_sale_serializer.data
        data['items_less_than_one'] = items_less_than_one
        data['items_greater_than_ten'] = items_greater_than_ten
        data['customers_without_purchase'] = customers_without_purchase
        data['employees_without_sale'] = employees_without_sale

        return response.Response(data, status=status.HTTP_200_OK)


class DashboardCategoryChartView(generics.ListAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated, IsSamlexAdmin]

    def get(self, request, *args, **kwargs):

        categories = Category.objects.filter(items__isnull=False).annotate(
            total_quantity=Sum(Case(
                When(items__quantity__gt=0, then=F('items__quantity')),
                default=Value(0),
                output_field=IntegerField()
            ))).order_by('-total_quantity')
        # print(categories)

        first_five_categories = categories[:5]
        first_five_sum = first_five_categories.aggregate(
            total_sum=Sum('total_quantity'))['total_sum']
        total_sum = categories.aggregate(
            total_sum=Sum('total_quantity'))['total_sum']
        #print("total sum", total_sum)
        #print("first_five_sum", first_five_sum)
        remaining_sum = total_sum - first_five_sum

        first_five_serializers = CategoryChartSerializer(
            first_five_categories, many=True)
        others = dict()
        others['name'] = 'others'
        others['total_quantity'] = remaining_sum
        # print("the firsr five", first_five_serializers.data)

        return response.Response({'first_five': first_five_serializers.data, 'others': others}, status=status.HTTP_200_OK)

        # categories_ordered_by_quantity = Category.objects.annotate(total_quantity=Sum('item__quantity')).order_by('-total_quantity')
