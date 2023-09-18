from etl_pipelines.models import ETFTransaction, Rule
from django.db.models.functions import TruncDate
from django.db.models import Count, Q
from datetime import datetime, date, time, timedelta
from django.utils import timezone


def get_fraud_dashboard_stats():
    result_data = dict()
    result_data["rules_count"] = Rule.objects.filter(active=True).count()

    # Get the datetime range for today
    today = date.today()
    start_of_day = datetime.combine(date.today(), time.min)
    end_of_day = datetime.combine(date.today(), time.max)

    # Get the total number of transactions for today
    total_transactions_today = ETFTransaction.objects.filter(
        transaction_created_at__gte=start_of_day,
        transaction_created_at__lte=end_of_day,
    ).count()

    # Get the number of suspected transactions for today
    suspected_transactions_today = ETFTransaction.objects.filter(
        Q(monitoring_comments__isnull=False) & ~Q(monitoring_comments=''),
        transaction_created_at__gte=start_of_day,
        transaction_created_at__lte=end_of_day,
    ).count()

    # Calculate the percentage of transactions that are suspected
    if total_transactions_today > 0:
        percentage_suspected = round(((suspected_transactions_today / total_transactions_today) * 100), 2)
    else:
        percentage_suspected = 0

    result_data["total_transactions_today"] = total_transactions_today
    result_data["suspected_transactions_today"] = suspected_transactions_today
    result_data["percentage_suspected"] = percentage_suspected

    # Get the datetime range for the last 30 days
    end_of_day = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    start_of_day = (end_of_day - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Get a list of dates within the last 30 days
    date_range = [start_of_day + timedelta(days=i) for i in range(30)]

    # Calculate statistics for each transaction type
    transaction_types = ["withdrawal", "transfer"]
    vas_transactions = ETFTransaction.objects.exclude(transaction_type__in=transaction_types)

    for transaction_type in transaction_types:
        result_data[transaction_type] = {
            'total_l30': {},
            'suspected_l30': {},
            'total': 0,
            'suspected': 0,
            'successful': 0,
            'failed': 0,
        }

        for date_day in date_range:
            next_date = date_day + timedelta(days=1)

            # Get the total number of transactions for the current day
            total_count = ETFTransaction.objects.filter(
                transaction_created_at__gte=date_day,
                transaction_type__icontains=transaction_type,
                transaction_created_at__lt=next_date
            ).count()

            # Get the total number of suspected transactions for the current day
            suspected_count = ETFTransaction.objects.filter(
                Q(monitoring_comments__isnull=False) & ~Q(monitoring_comments=''),
                Q(transaction_type__icontains=transaction_type),
                transaction_created_at__gte=date_day,
                transaction_created_at__lt=next_date,
            ).count()

            result_data[transaction_type]['total_l30'][date_day.strftime('%Y-%m-%d')] = total_count
            result_data[transaction_type]['suspected_l30'][date_day.strftime('%Y-%m-%d')] = suspected_count

            # Update the total and suspected counts for the last 30 days
            result_data[transaction_type]['total'] += total_count
            result_data[transaction_type]['suspected'] += suspected_count

        # Get the counts for the last 30 days
        transactions_last_30_days = ETFTransaction.objects.filter(
            transaction_created_at__gte=timezone.now() - timedelta(days=30),
            transaction_type__icontains=transaction_type
        ).count()

        suspected_transactions_last_30_days = ETFTransaction.objects.filter(
            Q(monitoring_comments__isnull=False) & ~Q(monitoring_comments=''),
            Q(transaction_type__icontains=transaction_type),
            transaction_created_at__gte=timezone.now() - timedelta(days=30),
        ).count()

        successful_transactions_last_30_days = ETFTransaction.objects.filter(
            transaction_type__icontains=transaction_type,
            transaction_created_at__gte=timezone.now() - timedelta(days=30),
            transaction_status__icontains='success'
        ).count()

        failed_transactions_last_30_days = ETFTransaction.objects.filter(
            transaction_type__icontains=transaction_type,
            transaction_created_at__gte=timezone.now() - timedelta(days=30),
            transaction_status__icontains='failed'
        ).count()

        result_data[transaction_type]['total'] = transactions_last_30_days
        result_data[transaction_type]['suspected'] = suspected_transactions_last_30_days
        result_data[transaction_type]['successful'] = successful_transactions_last_30_days
        result_data[transaction_type]['failed'] = failed_transactions_last_30_days

    # Calculate statistics for vas transactions
    result_data["vas"] = {
        'total_l30': {},
        'suspected_l30': {},
        'total': 0,
        'suspected': 0,
        'successful': 0,
        'failed': 0,
    }

    for date_day in date_range:
        next_date = date_day + timedelta(days=1)

        # Get the total number of vas transactions for the current day
        total_count = vas_transactions.filter(
            transaction_created_at__gte=date_day,
            transaction_created_at__lt=next_date
        ).count()

        # Get the total number of suspected vas transactions for the current day
        suspected_count = vas_transactions.filter(
            Q(monitoring_comments__isnull=False) & ~Q(monitoring_comments=''),
            transaction_created_at__gte=date_day,
            transaction_created_at__lt=next_date,
        ).count()

        result_data["vas"]['total_l30'][date_day.strftime('%Y-%m-%d')] = total_count
        result_data["vas"]['suspected_l30'][date_day.strftime('%Y-%m-%d')] = suspected_count

        # Update the total and suspected counts for the last 30 days
        result_data["vas"]['total'] += total_count
        result_data["vas"]['suspected'] += suspected_count

    # Get the counts for the last 30 days for vas transactions
    transactions_last_30_days = vas_transactions.filter(
        transaction_created_at__gte=timezone.now() - timedelta(days=30)
    ).count()

    suspected_transactions_last_30_days = vas_transactions.filter(
        Q(monitoring_comments__isnull=False) & ~Q(monitoring_comments=''),
        transaction_created_at__gte=timezone.now() - timedelta(days=30)
    ).count()

    successful_transactions_last_30_days = vas_transactions.filter(
        transaction_created_at__gte=timezone.now() - timedelta(days=30),
        transaction_status__icontains='success'
    ).count()

    failed_transactions_last_30_days = vas_transactions.filter(
        transaction_created_at__gte=timezone.now() - timedelta(days=30),
        transaction_status__icontains='failed'
    ).count()

    result_data["vas"]['total'] = transactions_last_30_days
    result_data["vas"]['suspected'] = suspected_transactions_last_30_days
    result_data["vas"]['successful'] = successful_transactions_last_30_days
    result_data["vas"]['failed'] = failed_transactions_last_30_days

    return result_data
