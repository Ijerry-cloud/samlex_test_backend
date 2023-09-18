from api.services.get_banks import PARAM_QUERY_BY_NAME
from etl_pipelines.models import MerchantSummary
from django.db.models import Q


PARAM_QUERY_BY_MERCHANT_NAME = 'merchant_name'
PARAM_QUERY_BY_MERCHANT_ID = 'merchant_id'
PARAM_QUERY_BY_RANGE = 'range'
PARAM_QUERY_BY_CREATED_AT = 'created'


def get_merchant_summaries(request):
    """
    
    """       
    # build this query lazily
    merchant_summaries = MerchantSummary.objects.all()
    
    if request.query_params.get(PARAM_QUERY_BY_RANGE):
        range_value = request.query_params.get(PARAM_QUERY_BY_RANGE)
        if range_value == 'l30':
            
            merchant_summaries = merchant_summaries.filter(
                Q(txn_vol_l30__isnull=False) |
                Q(txn_val_l30__isnull=False) |
                Q(txn_vol_success_l30__isnull=False) |
                Q(txn_val_success_l30__isnull=False) |
                Q(txn_vol_failed_l30__isnull=False) |
                Q(txn_val_failed_l30__isnull=False) 
            )       
        if range_value == 'all_time':
            
            merchant_summaries = merchant_summaries.filter(
                Q(txn_vol_alltime__isnull=False) |
                Q(txn_val_alltime__isnull=False) |
                Q(txn_vol_success_alltime__isnull=False) |
                Q(txn_val_success_alltime__isnull=False) |
                Q(txn_vol_failed_alltime__isnull=False) |
                Q(txn_val_failed_alltime__isnull=False) 
            )       
        if range_value == 'today':
            merchant_summaries = merchant_summaries.filter(
                Q(today_vol_success__isnull=False) |
                Q(today_val_success__isnull=False) |
                Q(today_vol_failed__isnull=False) |
                Q(today_val_failed__isnull=False) |
                Q(today_vol__isnull=False) |
                Q(today_val__isnull=False) 
            )   
        
    if request.query_params.get(PARAM_QUERY_BY_MERCHANT_NAME):
        merchant_summaries = merchant_summaries.filter(merchant__name__icontains=request.query_params.get(PARAM_QUERY_BY_MERCHANT_NAME))
    if request.query_params.get(PARAM_QUERY_BY_CREATED_AT):
        merchant_summaries = merchant_summaries.filter(created=request.query_params.get(PARAM_QUERY_BY_CREATED_AT))
    if request.query_params.get(PARAM_QUERY_BY_MERCHANT_ID):
        merchant_summaries = merchant_summaries.filter(merchant__mid__icontains=request.query_params.get(PARAM_QUERY_BY_MERCHANT_ID))

    return merchant_summaries
    