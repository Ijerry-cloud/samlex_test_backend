from etl_pipelines.models import ETFTransaction, Product
from django.db.models.functions import TruncDate
from django.db.models import Count

def fetch_txn_breakdown_by_type_stats(
    start_date,
    end_date
):
    """
  
    """
    result_data = list()

    transaction_types = Product.objects.values(
        'product_type'
        ).annotate(
            count=Count('product_type')
        )

    for transaction_type in transaction_types:
        data = dict()
        data['transaction_type'] = transaction_type.get("product_type")
        suspected_transactions = ETFTransaction.objects.filter(
            monitoring_comments__isnull=False,
            transaction_type=transaction_type.get("product_type"),
            transaction_created_at__range=[start_date, end_date]
        ).count()
        total_transactions = ETFTransaction.objects.filter(
            transaction_type=transaction_type.get("product_type"),
            transaction_created_at__range=[start_date, end_date]
        ).count()
        data['suspected_transactions'] = suspected_transactions
        data['total_transactions'] = total_transactions        

        result_data.append(data)
    return result_data