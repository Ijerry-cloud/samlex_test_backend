from etl_pipelines.models import BankSummary
from django.db.models import Q

PARAM_QUERY_BY_BANK_NAME = 'bank'
PARAM_QUERY_BY_BANK_CODE = 'code'
PARAM_QUERY_BY_CREATED_AT = 'created'
PARAM_QUERY_BY_RANGE = 'range'


def get_bank_summaries(request):
    """_summary_

    Args:
        request (_type_): _description_
    Queryset
    """
    
    # build this query lazily
    
    bank_summaries = BankSummary.objects.all()
    
    if request.query_params.get(PARAM_QUERY_BY_RANGE):
        range_value = request.query_params.get(PARAM_QUERY_BY_RANGE)
        if range_value == 'l30':
            
            bank_summaries = bank_summaries.filter(
                Q(txn_vol_l30__isnull=False) |
                Q(txn_val_l30__isnull=False) |
                Q(txn_vol_success_l30__isnull=False) |
                Q(txn_val_success_l30__isnull=False) |
                Q(txn_vol_failed_l30__isnull=False) |
                Q(txn_val_failed_l30__isnull=False) 
            )       
        if range_value == 'all_time':
            
            bank_summaries = bank_summaries.filter(
                Q(txn_vol_alltime__isnull=False) |
                Q(txn_val_alltime__isnull=False) |
                Q(txn_vol_success_alltime__isnull=False) |
                Q(txn_val_success_alltime__isnull=False) |
                Q(txn_vol_failed_alltime__isnull=False) |
                Q(txn_val_failed_alltime__isnull=False) 
            )       
        if range_value == 'today':
            bank_summaries = bank_summaries.filter(
                Q(today_vol_success__isnull=False) |
                Q(today_val_success__isnull=False) |
                Q(today_vol_failed__isnull=False) |
                Q(today_val_failed__isnull=False) |
                Q(today_vol__isnull=False) |
                Q(today_val__isnull=False) 
            )   
        
    if request.query_params.get(PARAM_QUERY_BY_BANK_NAME):
        bank_summaries = bank_summaries.filter(bank__name__icontains=request.query_params.get(PARAM_QUERY_BY_BANK_NAME))
    if request.query_params.get(PARAM_QUERY_BY_CREATED_AT):
        bank_summaries = bank_summaries.filter(created=request.query_params.get(PARAM_QUERY_BY_BANK_NAME))

    return bank_summaries