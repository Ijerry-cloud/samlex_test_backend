from etl_pipelines.models import ETFTransaction, Rule
from api.serializers import RuleSerializer
from django.db.models.functions import TruncDate
from django.db.models import Count

def fetch_rule_breakdown_stats(
    rules_ids,
    start_date,
    end_date
):
    """
        rules_ids - a list of ids that is fetched from the Rules models
        start_date - a start date it defaults to today if not provided
        end_date - a end date it defaults to today if not provided

        this function loops over the list of ids provided by the rules parameters
        and filters for transaction that occurred over the start date and end date
        and also violated that rule, and it gets the count of the violating transactions
        broken down by day, over that time frame. 

        this data is then presented to the frontend to enable construction
        of pie charts and bar charts that can visually represent this data.

        returns dict
    """
    result_data = list()
    for rule_id in rules_ids:
        data = dict()
        rule_instance = Rule.objects.filter(id=rule_id).first()
        if rule_instance:
            rule_data = RuleSerializer(rule_instance).data
            data["rule"] = rule_data

            # get the suspected transaction breakdown by date #
            suspected_etf_transactions = ETFTransaction.objects.filter(
                monitoring_comments__icontains=str(rule_instance.id),
                transaction_created_at__range=[start_date, end_date],
                transaction_type__icontains=str(rule_instance.product_type)
            ).values(
                'transaction_created_at__date'
            ).annotate(
                count=Count('id')
            ).values(
                'transaction_created_at__date', 'count'
            ).order_by('transaction_created_at__date')

            # get the total transaction breakdown by date #
            total_etf_transactions = ETFTransaction.objects.filter(
                transaction_created_at__range=[start_date, end_date]
            ).values(
                'transaction_created_at__date'
            ).annotate(
                count=Count('id')
            ).values(
                'transaction_created_at__date', 'count'
            ).order_by('transaction_created_at__date')
            
            # suspected transaction data #
            suspected_transaction = dict()            
            for txn in suspected_etf_transactions:
                suspected_transaction[str(txn.get("transaction_created_at__date"))] = txn.get("count")

            # total transaction data #
            total_transaction = dict()
            for txn in total_etf_transactions:
                total_transaction[str(txn.get("transaction_created_at__date"))] = txn.get("count")

            data["suspected_transaction"] = suspected_transaction
            data["total_transaction"] = total_transaction

            result_data.append(data)
    return result_data