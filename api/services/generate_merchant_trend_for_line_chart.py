from django.db.models.functions import TruncDate, TruncDay
from django.db.models import Sum, Count
from django.utils import timezone
from etl_pipelines.models import ETFTransaction, ETFUser
from datetime import datetime, timedelta

def generate_merchant_trend_for_line_chart(request):

    wallet_ids = request.GET.get('walletId', '')
    start_date = request.GET.get('startDate', '')
    end_date = request.GET.get('endDate', '')

    wallets = wallet_ids.split(',')
    
    data = []
    dates = []
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    
    for wallet_id in wallets:
        transactions = ETFTransaction.objects.filter(wallet_id=wallet_id, 
                                                   transaction_created_at__date__gte=start_date, 
                                                   transaction_created_at__date__lte=end_date)
        

        # Aggregate the transaction count and amount for each day
        daily_transactions = transactions.annotate(date=TruncDay('transaction_created_at')).values('date').annotate(
            count=Count('id'),
            amount=Sum('amount')
        )
        
        # Create a dictionary of counts and amounts for each date
        counts = {t['date'].strftime('%Y-%m-%d'): t['count'] for t in daily_transactions}
        amounts = {t['date'].strftime('%Y-%m-%d'): t['amount'] for t in daily_transactions}
        
        # Fill in missing dates with zeros
        for date in dates:
            if date not in counts:
                counts[date] = 0
            if date not in amounts:
                amounts[date] = 0
        
        # Sort the counts and amounts by date
        counts = [counts[date] for date in sorted(counts)]
        amounts = [amounts[date] for date in sorted(amounts)]
        
        data.append({
            'wallet_id': wallet_id,
            'counts': counts,
            'amounts': amounts,
            "dates": dates
        })
        
    return data
