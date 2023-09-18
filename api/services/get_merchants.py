from etl_pipelines.models import Merchant


PARAM_QUERY_BY_NAME = 'name'
PARAM_QUERY_BY_MID = 'mid'
PARAM_QUERY_BY_BAND = 'band'
PARAM_QUERY_BY_CUSTOMER = 'customer'
PARAM_QUERY_BY_TERMINAL_COUNT = 'terminal_count'
PARAM_QUERY_BY_TEMINAL_COUNT_GREATER_THAN = 'teminal_count_gt'
PARAM_QUERY_BY_TEMINAL_COUNT_LESS_THAN = 'teminal_count_lt'


def get_merchants(request):
    """
    function that handles the getting of merchants
    from the database
    
    Args:
        filters (_type_): _description_
    Returns:
        QuerySet
    """
    filters = dict()
    
    if request.query_params.get(PARAM_QUERY_BY_NAME):
        filters['name__icontains'] = request.query_params.get(PARAM_QUERY_BY_NAME)
    if request.query_params.get(PARAM_QUERY_BY_BAND):
        filters["band__icontains"] = request.query_params.get(PARAM_QUERY_BY_BAND)
    if request.query_params.get(PARAM_QUERY_BY_MID):
        filters["mid__icontains"] = request.query_params.get(PARAM_QUERY_BY_MID)
    if request.query_params.get(PARAM_QUERY_BY_CUSTOMER):
        filters["customer__icontains"] = request.query_params.get(PARAM_QUERY_BY_CUSTOMER)
    if request.query_params.get(PARAM_QUERY_BY_TERMINAL_COUNT):
        filters["terminal_count"] = request.query_params.get(PARAM_QUERY_BY_TERMINAL_COUNT)
    if request.query_params.get(PARAM_QUERY_BY_TEMINAL_COUNT_GREATER_THAN):
        filters["terminal_count__gt"] = request.query_params.get(PARAM_QUERY_BY_TEMINAL_COUNT_GREATER_THAN)
    if request.query_params.get(PARAM_QUERY_BY_TEMINAL_COUNT_LESS_THAN):
        filters["terminal_count__lt"] = request.query_params.get(PARAM_QUERY_BY_TEMINAL_COUNT_LESS_THAN)
        
    
    return Merchant.objects.filter(**filters)