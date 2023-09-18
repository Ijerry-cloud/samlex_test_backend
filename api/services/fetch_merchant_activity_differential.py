from django.db.models import F, Sum, Count
from datetime import timedelta
from django.db.models.functions import TruncDate, TruncDay
from django.utils import timezone
from etl_pipelines.models import ETFTransaction, ETFUser
from datetime import datetime, timedelta


def get_wallet_activity_by_differential(start_date, end_date, differential):
    # Group transactions by day and calculate the cumulative count and amount for each day
    transactions = ETFTransaction.objects.filter(
        transaction_created_at__date__range=[start_date, end_date]
    ).annotate(
        date=TruncDate('transaction_created_at')
    ).values(
        'wallet_id', 'date'
    ).annotate(
        cumulative_count=Count('id'),
        cumulative_amount=Sum('amount')
    ).order_by('wallet_id', 'date')

    # Create dictionary to hold data for each wallet ID
    wallet_data = {}

    # Loop through each wallet ID and calculate the differential between each day
    for wallet in transactions.values_list('wallet_id', flat=True).distinct():
        # Get the transactions for the current wallet ID
        wallet_transactions = transactions.filter(wallet_id=wallet)

        # Loop through each day and compare the cumulative count and amount with the next day
        count_data = []
        amount_data = []

        for i in range(1, len(wallet_transactions)):
            # Calculate the differential between the cumulative count for the current day and the next day
            curr_count = wallet_transactions[i-1]['cumulative_count']
            next_count = wallet_transactions[i]['cumulative_count']
            count_diff = (next_count - curr_count) / curr_count * 100

            # Calculate the differential between the cumulative amount for the current day and the next day
            curr_amount = wallet_transactions[i-1]['cumulative_amount']
            next_amount = wallet_transactions[i]['cumulative_amount']
            amount_diff = (next_amount - curr_amount) / curr_amount * 100

            # Check if the differential is met and add data to wallet_data dictionary if so
            if count_diff >= differential:
                count_data.append((wallet_transactions[i-1]['date'], wallet_transactions[i]['date'], count_diff))

            if amount_diff >= differential:
                amount_data.append((wallet_transactions[i-1]['date'], wallet_transactions[i]['date'], amount_diff))

        if count_data:
            wallet_data[wallet] = {
                'type': 'transaction_count',
                'data': count_data
            }

        if amount_data:
            wallet_data[wallet] = {
                'type': 'transaction_amount',
                'data': amount_data
            }

    return wallet_data
