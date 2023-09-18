from etl_pipelines.models import Bank


PARAM_QUERY_BY_NAME = 'name'
PARAM_QUERY_BY_CODE = 'code'

def get_banks(request):
    """
    function that handles the getting of banks
    from the database
    
    Args:
        filters (_type_): _description_
    Returns:
        QuerySet
    """
    filters = dict()
    
    if request.query_params.get(PARAM_QUERY_BY_NAME):
        filters['name__icontains'] = request.query_params.get(PARAM_QUERY_BY_NAME)
    if request.query_params.get(PARAM_QUERY_BY_CODE):
        filters["code__icontains"] = request.query_params.get(PARAM_QUERY_BY_CODE)
    
    return Bank.objects.filter(**filters)




# 
# [
    #
    # 'journals', -> 1672825 records
    # 'bands',  -> this collection is empty
    # 'banksummaries', -> 40974 records
    # 'registerednotifications', -> this collection is empty
    # 'bankconfigs', -> this collection has 3 items ()
    # 'merchantsummaries', 274342 records, i believe this translates to the Customer Manager
    # 'users', -> has only 2 records
    # 'terminalstates', -> 135039 records
    # 'terminalkeys' -> 3114 records
    # ]
#


#
# implememt authentication apis ( login, logout, change_password, create user )
# implement reporting apis
#

# get banks
# get merchants
# get bank summaries
# get merchant summaries

###########################################
# what of customer and terminal
###########################################