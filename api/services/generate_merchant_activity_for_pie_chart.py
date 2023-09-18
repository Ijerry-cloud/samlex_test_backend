from django.db.models import Count, Sum
from decimal import Decimal
from django.db.models.functions import TruncDate, TruncDay
from django.utils import timezone
from etl_pipelines.models import ETFTransaction, ETFUser
from datetime import datetime, timedelta

def get_pie_chart_transaction_activity(start_date, end_date):
    transactions = ETFTransaction.objects.filter(transaction_created_at__range=(start_date, end_date))
    wallet_ids = transactions.values_list('wallet_id', flat=True).distinct()
    
    activity_by_count = []
    activity_by_amount = []
    for wallet_id in wallet_ids:
        wallet_transactions = transactions.filter(
            wallet_id=wallet_id,
            transaction_created_at__range=(start_date, end_date)
        )
        count = wallet_transactions.count()
        amount = wallet_transactions.aggregate(total=Sum('amount'))['total'] or Decimal(0)
        activity_by_count.append({'wallet_id': wallet_id, 'count': count})
        activity_by_amount.append({'wallet_id': wallet_id, 'amount': amount})
        
    return {'activity_by_count': activity_by_count, 'activity_by_amount': activity_by_amount}
