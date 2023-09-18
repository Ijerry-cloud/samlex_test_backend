from django.http import JsonResponse
from django.db.models import Count, Sum, IntegerField
from django.db.models.functions import Coalesce, Cast
from django.utils import timezone
from datetime import datetime
from etl_pipelines.models import ETFTransaction, ETFUser


def fetch_merchants_plot(request):
    merchant_limit = request.GET.get('merchantLimit')
    merchant_type = request.GET.get('type')
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    # Get all transactions between start_date and end_date
    transactions = ETFTransaction.objects.filter(transaction_created_at__gte=start_date, transaction_created_at__lte=end_date)

    # Aggregate transactions by merchant (wallet_id)
    transaction_counts = transactions.values('wallet_id').annotate(
        count=Coalesce(Count('id'), 0)
    )

    transaction_amounts = transactions.values('wallet_id').annotate(
        amount=Cast(Coalesce(Sum('amount'), 0), IntegerField())
    )

    # Sort merchants by count or amount, depending on merchant_type
    if merchant_type == 'top':
        transaction_counts = transaction_counts.order_by('-count')
        transaction_amounts = transaction_amounts.order_by('-amount')
    else:
        transaction_counts = transaction_counts.order_by('count')
        transaction_amounts = transaction_amounts.order_by('amount')
    
    # Get top or bottom n merchants, depending on merchant_limit
    merchant_limit = int(request.GET.get('merchantLimit', '10'))
    transaction_counts = transaction_counts[:merchant_limit]
    transaction_amounts = transaction_amounts[:merchant_limit]

    # Get the merchant data from ETFUser table
    merchants_data = ETFUser.objects.all()
    merchants_dict = {merchant.data.get('walletId', 'xxx'): {
        "businessName": merchant.data.get("businessName"),
        "firstName": merchant.data.get("firstName"),
        "lastName": merchant.data.get("lastName"),
        "username": merchant.data.get("username"),
    } for merchant in merchants_data}
    
    # Build response
    response = {
        'series_count': [],
        'series_amount': [],
    }
    for metric_type in ['count', 'amount']:
        metric_name = 'transaction_' + metric_type
        n_merchants = []
        if metric_type == 'count':
            for transaction_count in transaction_counts:
                merchant_data = merchants_dict.get(transaction_count['wallet_id'], {})
            
                n_merchants.append({
                    'merchant': merchant_data,
                    metric_name: transaction_count[metric_type],
                    'wallet_id': transaction_count['wallet_id'],
                })
            response['series_count'].append({
                'name': metric_name,
                'data': n_merchants
            })
        if metric_type == 'amount':
            for transaction_amount in transaction_amounts:
                merchant_data = merchants_dict.get(transaction_amount['wallet_id'], {})
            
                n_merchants.append({
                    'merchant': merchant_data,
                    metric_name: transaction_amount[metric_type],
                    'wallet_id': transaction_amount['wallet_id'],
                })
            response['series_amount'].append({
                'name': metric_name,
                'data': n_merchants
            })
    return response
