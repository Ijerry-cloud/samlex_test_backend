from rest_framework.serializers import ModelSerializer, StringRelatedField, SerializerMethodField
from etl_pipelines.models import *
from accounts.serializers import UserSerializer

class BankSerializer(ModelSerializer):
    
    class Meta:
        model = Bank
        fields = '__all__'
        
        
class MerchantSerializer(ModelSerializer):
    
    class Meta:
        model = Merchant
        fields = '__all__'
        
        
class MerchantSummarySerializer(ModelSerializer):
    
    merchant = SerializerMethodField()
    
    class Meta:
        model = MerchantSummary
        fields = '__all__'
        
    def get_merchant(self, obj):
        merchant = obj.merchant
        if merchant:
            return { "name": merchant.name, "mid": merchant.mid }
        return { "name": "", "mid": "" }
        
        
class BankSummarySerializer(ModelSerializer):
    
    bank = StringRelatedField()
    
    class Meta:
        model = BankSummary
        fields = '__all__'


class RuleSerializer(ModelSerializer):

    rule_value = SerializerMethodField()
    product = SerializerMethodField()
    manageable_value = SerializerMethodField()
    warning_value = SerializerMethodField()
    danger_value = SerializerMethodField()
    manageable_actors = SerializerMethodField()
    warning_actors = SerializerMethodField()
    danger_actors = SerializerMethodField()

    class Meta:
        model = Rule
        fields = '__all__'

    def get_rule_value(self, rule):
        return rule.value
    
    def get_product(self, rule):
        return rule.product_type

    def get_manageable_value(self, rule):
        threshold = Threshold.objects.filter(rule=rule, level="manageable").first()
        if threshold:
            return threshold.value
        return None

    def get_warning_value(self, rule):
        threshold = Threshold.objects.filter(rule=rule, level="warning").first()
        if threshold:
            return threshold.value
        return None

    def get_danger_value(self, rule):
        threshold = Threshold.objects.filter(rule=rule, level="danger").first()
        if threshold:
            return threshold.value
        return None
    
    def get_manageable_actors(self, rule):
        threshold = Threshold.objects.filter(rule=rule, level="manageable").first()
        thresholds = ThresholdEmails.objects.filter(
            threshold=threshold
        )
        users = [thresh.user for thresh in thresholds]
        user_serializer = UserSerializer(users, many=True)
        return user_serializer.data

    def get_warning_actors(self, rule):
        threshold = Threshold.objects.filter(rule=rule, level="warning").first()
        thresholds = ThresholdEmails.objects.filter(
            threshold=threshold
        )
        users = [thresh.user for thresh in thresholds]
        user_serializer = UserSerializer(users, many=True)
        return user_serializer.data

    def get_danger_actors(self, rule):
        threshold = Threshold.objects.filter(rule=rule, level="danger").first()
        thresholds = ThresholdEmails.objects.filter(
            threshold=threshold
        )
        users = [thresh.user for thresh in thresholds]
        user_serializer = UserSerializer(users, many=True)
        return user_serializer.data



class TransactionSerializer(ModelSerializer):

    monitoring_comments_detail = SerializerMethodField()
    wallet_details = SerializerMethodField()

    class Meta:
        model = ETFTransaction
        fields = '__all__'

    def get_monitoring_comments_detail(self, instance):

        rules = list()
        if instance.monitoring_comments:
            for rule_id in instance.monitoring_comments.split(','):
                rule = Rule.objects.filter(id=rule_id).first()
                if rule:
                    rules.append(rule.description)

            return rules
        return []
    
    def get_wallet_details(self, instance):
        etf_user = ETFUser.objects.filter(data__walletId=instance.wallet_id).first()
        return etf_user.data if etf_user else {}

class MerchantMetricSerializer(ModelSerializer):

    no_of_days = SerializerMethodField()
    percentage_violation = SerializerMethodField()
    notification_emails = SerializerMethodField()

    class Meta:
        model = MerchantMetric
        exclude = ['name']

    def get_no_of_days(self, instance):
        return instance.no_of_days
    
    def get_percentage_violation(self, instance):
        return instance.percentage_violation
    
    def get_notification_emails(self, instance):
        MerchantMetricEmails = MerchantMetricEmail.objects.filter(merchant_metric = instance)
        users = [merchant.user for merchant in MerchantMetricEmails]
        user_serializer = UserSerializer(users, many=True)
        return user_serializer.data