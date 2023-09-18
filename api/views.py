from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, response
from rest_framework.permissions import IsAuthenticated
from  accounts.authentication import BearerTokenAuthentication
from etl_pipelines.models import Rule, ETFTransaction, Product, Threshold, ThresholdEmails, MerchantMetric, MerchantMetricEmail
from api.services.get_banks import get_banks
from api.services.get_merchant_summaries import get_merchant_summaries
from api.services.get_bank_summaries import get_bank_summaries
from api.services.get_merchants import get_merchants
from api.services.get_bank_summaries_chart import get_bank_summaries_chart
from api.services.get_transactions import get_transactions, get_suspected_transactions
from api.services.get_rules import get_rules
from api.services.fetch_rule_breakdown_stats import fetch_rule_breakdown_stats
from api.services.fetch_txn_breakdown_by_type_stats import fetch_txn_breakdown_by_type_stats
from api.services.get_fraud_dashboard_stats import get_fraud_dashboard_stats
from api.services.fetch_merchants_plot import fetch_merchants_plot
from api.services.fetch_merchants import get_merchants_list
from api.services.generate_merchant_trend_for_line_chart import generate_merchant_trend_for_line_chart
from api.services.generate_merchant_activity_for_pie_chart import get_pie_chart_transaction_activity
from api.services.fetch_merchant_activity_differential import get_wallet_activity_by_differential
from etl_pipelines.utils.pagination import CustomPagination
from django.db.models import Count
from .serializers import (
    BankSerializer,
    MerchantSerializer,
    MerchantSummarySerializer,
    BankSummarySerializer,
    TransactionSerializer,
    RuleSerializer,
    MerchantMetricSerializer
    )
from datetime import datetime, time
from django.contrib.auth import get_user_model
from accounts.serializers import UserSerializer
from django.db import transaction

User = get_user_model()

# Create your views here.
class BankApiView(generics.ListAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        banks = get_banks(request)
        bank_serializer = BankSerializer(self.paginate_queryset(banks), many=True)
        
        return self.paginator.get_paginated_response(bank_serializer.data)
    
    
class MerchantApiView(generics.ListAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        merchants = get_merchants(request)
        merchant_serializer = MerchantSerializer(self.paginate_queryset(merchants), many=True)
        
        return self.paginator.get_paginated_response(merchant_serializer.data)
    

class BankSummaryApiView(generics.ListAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        
        bank_summaries = get_bank_summaries(request)
        bank_serializer = BankSummarySerializer(self.paginate_queryset(bank_summaries), many=True)
        
        return self.paginator.get_paginated_response(bank_serializer.data)
    
    
class MerchantSummaryApiView(generics.ListAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        merchant_summaries = get_merchant_summaries(request)
        merchant_serializer = MerchantSummarySerializer(self.paginate_queryset(merchant_summaries), many=True)
        
        return self.paginator.get_paginated_response(merchant_serializer.data)


class BankSummaryChartApiView(generics.ListAPIView):

    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        
        bank_id = self.kwargs.get("id")
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        result = get_bank_summaries_chart(bank_id, start_date, end_date)
        
        return response.Response(
            {"message": "success", "data": result}, 
            status=status.HTTP_200_OK
        )


class TransactionApiView(generics.ListAPIView):

    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        
        print(request.query_params.get('rule_id'), request.query_params.get("product_type"))
        if request.query_params.get('rule_id') or request.query_params.get("product_type"):
            print('xx')
            transactions = get_suspected_transactions(request)
        else:
            print('yy')
            transactions = get_transactions(request)


        transaction_serializer = TransactionSerializer(self.paginate_queryset(transactions), many=True)
        
        return self.paginator.get_paginated_response(transaction_serializer.data)


class ETFTransactionStatView(generics.ListAPIView):

    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        # build the rules data
        rules_data = RuleSerializer(Rule.objects.filter(active=True), many=True).data

        # build the product
        transaction_types = ETFTransaction.objects.values(
            'transaction_type'
            ).order_by(
                'transaction_type'
                ).annotate(count=Count('transaction_type'))

        products = ETFTransaction.objects.values('product'
            ).order_by('product'
            ).annotate(count=Count('product'))

        payment_method = ETFTransaction.objects.values(
            'payment_method'
            ).order_by('payment_method'
            ).annotate(count=Count('payment_method'))

        data = dict()
        data['transaction_types'] = transaction_types
        data['products'] = products
        data['payment_method'] = payment_method
        data['rules_data'] = rules_data
        return response.Response(data, status=status.HTTP_200_OK)


class ETFTransactionTypeBreakdownView(generics.ListAPIView):

    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        result_data = dict()
        result_data["message"] = "success"

        # get the start date and end date
        # and convert it to datetime format
        start_date = request.query_params.get("startDate")
        end_date = request.query_params.get("endDate")
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        start_date = datetime.combine(start_date, time.min) if start_date else datetime.now()
        end_date = datetime.combine(end_date, time.max) if end_date else datetime.now()

        data = fetch_txn_breakdown_by_type_stats(start_date, end_date)

        result_data["data"] = data

       
        return response.Response(result_data, status=status.HTTP_200_OK)


class ETFTransactionRuleBreakdownView(generics.ListAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        result_data = dict()
        result_data["message"] = "success"

        # get the start date and end date
        # and convert it to datetime format
        start_date = request.query_params.get("startDate")
        end_date = request.query_params.get("endDate")
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        start_date = datetime.combine(start_date, time.min) if start_date else datetime.now()
        end_date = datetime.combine(end_date, time.max) if end_date else datetime.now()

        rule_ids = request.query_params.get('selectedRules').split(',')

        data = fetch_rule_breakdown_stats(
            rule_ids,
            start_date,
            end_date
            )

        result_data["data"] = data

        return response.Response(result_data, status=status.HTTP_200_OK)


class DeactivateRuleView(generics.CreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        rules = Rule.objects.filter(id__in=request.data.get("selected"))
        for rule in rules:
            rule.active = False
            rule.updated_by = request.user
            rule.save()
        return response.Response({"message": "successfully deactivated"}, status=status.HTTP_200_OK)


class ActivateRuleView(generics.CreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        rules = Rule.objects.filter(id__in=request.data.get("selected"))
        for rule in rules:
            rule.active = True
            rule.updated_by = request.user
            rule.save()
        return response.Response({"message": "successfully activated"}, status=status.HTTP_200_OK)


class ETFFraudDashboardView(generics.ListAPIView):

    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        result_data = dict()
        result_data["message"] = "success"

        data = get_fraud_dashboard_stats()

        result_data["data"] = data

        return response.Response(result_data, status=status.HTTP_200_OK)


class ETFRulesView(generics.ListCreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        rules = get_rules(request)
        rule_serializer = RuleSerializer(self.paginate_queryset(rules), many=True)
        
        return self.paginator.get_paginated_response(rule_serializer.data)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        
        rule_instance = Rule.objects.create(
            description=request.data.get("description"),
            product_type=request.data.get("product"),
            condition=request.data.get("condition"),
            value=request.data.get("rule_value"),
            value2=request.data.get("rule_value2"),
            created_by=request.user,
            updated_by=request.user
        )

        # create user to be notified
        selected_manageable = request.data.get("selectedManageable")
        selected_warning = request.data.get("selectedWarning")
        selected_danger = request.data.get("selectedDanger")

        notification_levels = [
            "manageable",
            "warning",
            "danger"
        ]

        notification_values = [
            request.data.get("manageable_value"), 
            request.data.get("warning_value"), 
            request.data.get("danger_value"), 
            ]

        notification_users = [
            selected_manageable,
            selected_warning,
            selected_danger
        ]

        for count in range(3):
            threshold = Threshold.objects.create(
                rule=rule_instance,
                value=notification_values[count],
                level=notification_levels[count],
                created_by=request.user,
                updated_by=request.user
            )

            for notification_user in notification_users[count]:
                user_instance = User.objects.filter(email=notification_user.get("email")).first()
                if user_instance:
                    ThresholdEmails.objects.create(
                        threshold=threshold,
                        user=user_instance,
                        level=notification_levels[count]
                    )

        return response.Response({"message": "successful"}, status=status.HTTP_201_CREATED)


class RulePrerequisitesView(generics.ListAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        products = Product.objects.values('product_type'
            ).order_by('product_type'
            ).annotate(count=Count('product_type'))
        
        users = User.objects.filter(is_active=True)
        user_serializer = UserSerializer(users, many=True)

        data = dict()
        data["products"] = products
        data["users"] = user_serializer.data
        return response.Response(data, status=status.HTTP_200_OK)


class EditRuleView(generics.ListCreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = dict()
        rule_instance = get_object_or_404(Rule, pk=self.kwargs.get("id"))
        rule = RuleSerializer(rule_instance)

        data["message"] = "success"
        data["data"] = rule.data

        return response.Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        rule_instance = get_object_or_404(Rule, pk=self.kwargs.get("id"))

        # create user to be notified
        selected_manageable = request.data.get("selectedManageable")
        selected_warning = request.data.get("selectedWarning")
        selected_danger = request.data.get("selectedDanger")

        notification_levels = [
            "manageable",
            "warning",
            "danger"
        ]

        notification_values = [
            request.data.get("manageable_value"), 
            request.data.get("warning_value"), 
            request.data.get("danger_value"), 
            ]
        
        # print('n-> ', notification_values, notification_count)

        notification_users = [
            selected_manageable,
            selected_warning,
            selected_danger
        ]

        for count in range(3):
            # check if there is a threshold for each level
            threshold = Threshold.objects.filter(
                rule=rule_instance,
                level=notification_levels[count]
                ).first()
            if not threshold:
                # if the threshold does not exist create it
                threshold = Threshold.objects.create(
                    rule=rule_instance,
                    value=notification_values[count],
                    level=notification_levels[count],
                    created_by=request.user,
                    updated_by=request.user
                )
            else:
                threshold.value = notification_values[count]
                threshold.last_updated_by = request.user
                threshold.save()
            # delete the notification threshold emails
            ThresholdEmails.objects.filter(threshold=threshold, level=notification_levels[count]).delete()

            for notification_user in notification_users[count]:
                
                user_instance = User.objects.filter(email=notification_user.get("email")).first()              
                if user_instance:
                    ThresholdEmails.objects.create(
                        threshold=threshold,
                        user=user_instance,
                        level=notification_levels[count]
                    )

        return response.Response({"message": "successful"}, status=status.HTTP_201_CREATED)


class FetchMerchantsAPIView(generics.ListAPIView):

    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs): 
        data = get_merchants_list()
        return response.Response(data, status=status.HTTP_200_OK)


class GenerateMerchantTrendForLineChart(generics.ListAPIView):

    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs): 
        data = generate_merchant_trend_for_line_chart(request)
        return response.Response(data, status=status.HTTP_200_OK)
    

class GeneratePieChartActivityAPIView(generics.ListAPIView):

    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs): 
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')
        
        data = get_pie_chart_transaction_activity(start_date, end_date)
        return response.Response({
            "data": data,
            "message": "success"
        }, status=status.HTTP_200_OK)


class GenerateMerchantDifferentialLineChartAPIView(generics.ListAPIView):

    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs): 
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        differential = request.GET.get('differential', 50)

        data = get_wallet_activity_by_differential(start_date, end_date, int(differential))
        return response.Response({
            "data": data,
            "message": "success"
        }, status=status.HTTP_200_OK)


class FetchMerchantVolumeForBarPlot(generics.ListAPIView):
    
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs): 
        merchant_limit = request.GET.get('merchantLimit')
        merchant_type = request.GET.get('type')
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')

        if not merchant_limit or not merchant_type or not start_date or not end_date:
            return response.Response({"message": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST)   

        try:
            merchant_limit = int(merchant_limit)
        except ValueError:
            return response.Response({"message": "Invalid type parameter"}, status=status.HTTP_400_BAD_REQUEST)

        if merchant_type not in ['top', 'bottom']:
            return response.Response({'message': 'Invalid type parameter'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
        except ValueError:
            return response.Response({'message': 'Invalid date format, use ISO 8601 format'}, status=status.HTTP_400_BAD_REQUEST)


        data = fetch_merchants_plot(request)
        return response.Response(data, status=status.HTTP_200_OK)


class EditMerchantMonitoringMetricView(generics.ListCreateAPIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        
        data = dict()
        users = User.objects.filter(is_active=True)
        user_serializer = UserSerializer(users, many=True)

        merchant_metric_instance = MerchantMetric.objects.filter(name="merchant_monitoring_metrics").first()
        if not merchant_metric_instance:
            return response.Response({"message": "not found"}, status=status.HTTP_404_NOT_FOUND)
        
        merchant_metric = MerchantMetricSerializer(merchant_metric_instance)

        data["message"] = "success"
        data["data"] = merchant_metric.data
        data["users"] = user_serializer.data

        return response.Response(data, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        merchant_metric = MerchantMetric.objects.filter(name="merchant_monitoring_metrics").first()
        if not merchant_metric:
            return response.Response({"message": "not found"}, status=status.HTTP_404_NOT_FOUND)

        selected_emails = request.data.get("selectedEmails")
        no_of_days = request.data.get("no_of_days")
        percentage_violation = request.data.get("percentage_violation")
        minimum_amount  = request.data.get("minimum_amount")
        sending_intervals = request.data.get("sending_intervals")

        if merchant_metric:
            merchant_metric.no_of_days = no_of_days
            merchant_metric.percentage_violation = percentage_violation
            merchant_metric.minimum_amount = minimum_amount
            merchant_metric.sending_intervals = sending_intervals
            merchant_metric.save()
        else:
            #create the metric instance
            merchant_metric = MerchantMetric.objects.create(
                no_of_days = no_of_days,
                percentage_violation = percentage_violation,
                minimum_amount = minimum_amount,
                sending_intervals = sending_intervals,
                name = "merchant_monitoring_metrics"
            )

        #delete the notification emails
        MerchantMetricEmail.objects.filter(merchant_metric = merchant_metric).delete()

        for notification_user in selected_emails:
            user_instance = User.objects.filter(email=notification_user.get("email")).first()
            if user_instance:
                MerchantMetricEmail.objects.create(
                    user = user_instance,
                    merchant_metric = merchant_metric
                )

        return response.Response({"message": "successful"}, status=status.HTTP_201_CREATED)


class SampleView(generics.ListAPIView):
    

    def get(self, request, *args, **kwargs):

        return render(request, template_name='TransactionAlert/index.html', context={
            "top_merchant_offenders": [
                {
                    "name": "Apples"
                }
            ]
            })
