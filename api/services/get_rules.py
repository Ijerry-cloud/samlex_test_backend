from etl_pipelines.models import Merchant, Rule

PARAM_QUERY_BY_DESCRIPTION = 'description'

def get_rules(request):
    """
    function that handles the getting of rules
    from the database
    
    Args:
        filters (_type_): _description_
    Returns:
        QuerySet
    """
    filters = dict()
    
    if request.query_params.get(PARAM_QUERY_BY_DESCRIPTION):
        filters['description__icontains'] = request.query_params.get(PARAM_QUERY_BY_DESCRIPTION)    
    
    return Rule.objects.filter(**filters).order_by("-created_at").order_by("-active")