from datetime import datetime, time
from etl_pipelines.models import BankSummary
from django.db.models import Q


def get_bank_summaries_chart(id, start_date, end_date):
    """Get bank summary charts graph
    
    """
    start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
    end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    start_date = datetime.combine(start_date, time.min) if start_date else datetime.now()
    end_date = datetime.combine(end_date, time.max) if end_date else datetime.now()

    result = dict()

    # build this query lazily
    bank_summaries = BankSummary.objects.filter(bank=id)

    # run the first query for daily
    today_bank_summaries = bank_summaries.filter(
                Q(today_vol_success__isnull=False) |
                Q(today_val_success__isnull=False) |
                Q(today_vol_failed__isnull=False) |
                Q(today_val_failed__isnull=False) |
                Q(today_vol__isnull=False) |
                Q(today_val__isnull=False) 
            )
    print(today_bank_summaries.count())
    today_bank_summaries = today_bank_summaries.filter(created__range=[start_date, end_date]).order_by("id")
    print(today_bank_summaries.count())

    today = dict()
    for today_summary in today_bank_summaries:
        data = dict()
        data['vol_success'] = today_summary.today_vol_success
        data['vol_failed'] = today_summary.today_vol_failed
        data['total_vol'] = today_summary.today_vol
        data['val_success'] = today_summary.today_val_success
        data['val_failed'] = today_summary.today_val_failed
        data['total_val'] = today_summary.today_val
        today[str(today_summary.created.date())] = data

    # run the next query for last 30 days
    l30_bank_summaries = bank_summaries.filter(
        Q(txn_vol_l30__isnull=False) |
        Q(txn_val_l30__isnull=False) |
        Q(txn_vol_success_l30__isnull=False) |
        Q(txn_val_success_l30__isnull=False) |
        Q(txn_vol_failed_l30__isnull=False) |
        Q(txn_val_failed_l30__isnull=False)
    )

    print(l30_bank_summaries.count())
    l30_bank_summaries = l30_bank_summaries.filter(created__range=[start_date, end_date]).order_by("id")
    print(l30_bank_summaries.count())

    l30 = dict()
    for l30_summary in l30_bank_summaries:
        data = dict()
        data['vol_success'] = l30_summary.txn_vol_success_l30
        data['vol_failed'] = l30_summary.txn_vol_failed_l30
        data['total_vol'] = l30_summary.txn_vol_l30
        data['val_success'] = l30_summary.txn_val_success_l30
        data['val_failed'] = l30_summary.txn_val_failed_l30
        data['total_val'] = l30_summary.txn_val_l30
        l30[str(l30_summary.created.date())] = data

    # run the next query for all time
    all_time_bank_summaries = bank_summaries.filter(
                Q(txn_vol_alltime__isnull=False) |
                Q(txn_val_alltime__isnull=False) |
                Q(txn_vol_success_alltime__isnull=False) |
                Q(txn_val_success_alltime__isnull=False) |
                Q(txn_vol_failed_alltime__isnull=False) |
                Q(txn_val_failed_alltime__isnull=False) 
            ) 

    print(all_time_bank_summaries.count())
    all_time_bank_summaries = all_time_bank_summaries.filter(created__range=[start_date, end_date]).order_by("id")
    print(all_time_bank_summaries.count())
    all_time = dict()
    for all_time_summary in all_time_bank_summaries:
        data = dict()
        data['vol_success'] = all_time_summary.txn_vol_success_alltime
        data['vol_failed'] = all_time_summary.txn_vol_failed_alltime
        data['total_vol'] = all_time_summary.txn_vol_alltime
        data['val_success'] = all_time_summary.txn_val_success_alltime
        data['val_failed'] = all_time_summary.txn_val_failed_alltime
        data['total_val'] = all_time_summary.txn_val_alltime
        all_time[str(all_time_summary.created.date())] = data
        
    result['daily'] = today
    result['l30'] = l30
    result['all_time'] = all_time

    return result


