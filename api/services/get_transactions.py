from etl_pipelines.models import ETFTransaction
from django.db.models import Q

PARAM_ACCOUNT = 'account'
PARAM_TRANSACTION_TYPE = 'transaction_type'
PARAM_ACCOUNT_TYPE = 'account_type'
PARAM_WALLET_ID =   'wallet_id'
PARAM_CHANNEL = 'channel'
PARAM_TRANSACTION_STATUS = 'transaction_status'
PARAM_REVERSAL = 'reversal'
PARAM_CREDIT_STATUS = 'credit_status'
PARAM_PAYMENT_METHOD = 'payment_method'
PARAM_DESCRIPTION = 'description'
PARAM_MONITORING_COMMENTS = 'monitoring_comments'
PARAM_MONITORING_STATUS = 'monitoring_status'
PARAM_PRODUCT = 'product'
PARAM_PROVIDER = 'provider'
PARAM_TRANSACTION_DATE = 'transaction_date'
PARAM_TRANSACTION_TYPE = 'transaction_type'
PARAM_TRANSACTION_REFERENCE = 'transaction_reference'
# from here on are json fields
PARAM_TRANSACTION_PAN = 'pan'
PARAM_RRN_TRANSACTION = 'rrn_transaction'
PARAM_MERCHANT_NAME = 'merchant_name'
PARAM_MERCHANT_ADDRESS ='merchant_address'
PARAM_TERMINAL_ID = 'terminal_id'
PARAM_MERCHANT_ID ='merchant_id'

PARAM_ORIGINAOR_ACCOUNT_NAME = 'originator_account_name'
PARAM_ORIGINAOR_ACCOUNT_NUMBER = 'originator_account_number'
PARAM_BENEFICIARY_ACCOUNT_NAME = 'beneficiary_account_name'
PARAM_BENEFICIARY_ACCOUNT_NUMBER = 'beneficiary_account_number'

def get_transactions(request):
    """
    function that handles the getting of transactions
    from the database
    
    Args:
        filters (_type_): _description_
    Returns:
        QuerySet
    """
    filters = dict()
    
    if request.query_params.get(PARAM_ACCOUNT):
        filters['account__icontains'] = request.query_params.get(PARAM_ACCOUNT)
    if request.query_params.get(PARAM_TRANSACTION_TYPE):
        filters['transaction_type__icontains'] = request.query_params.get(PARAM_TRANSACTION_TYPE)
    if request.query_params.get(PARAM_ACCOUNT_TYPE):
        filters['account_type__icontains'] = request.query_params.get(PARAM_ACCOUNT_TYPE)
    if request.query_params.get(PARAM_WALLET_ID):
        filters['wallet_id__icontains'] = request.query_params.get(PARAM_WALLET_ID)
    if request.query_params.get(PARAM_CHANNEL):
        filters['channel__icontains'] = request.query_params.get(PARAM_CHANNEL)
    if request.query_params.get(PARAM_TRANSACTION_STATUS):
        filters['transaction_status__icontains'] = request.query_params.get(PARAM_TRANSACTION_STATUS)
    if request.query_params.get(PARAM_REVERSAL):
        # this is a boolean value
        filters['reversal__icontains'] = request.query_params.get(PARAM_REVERSAL)
    if request.query_params.get(PARAM_CREDIT_STATUS):
        # this is a boolean value
        filters['credit_status__icontains'] = request.query_params.get(PARAM_CREDIT_STATUS)
    if request.query_params.get(PARAM_PAYMENT_METHOD):
        filters['payment_method__icontains'] = request.query_params.get(PARAM_PAYMENT_METHOD)
    if request.query_params.get(PARAM_DESCRIPTION):
        filters['description__icontains'] = request.query_params.get(PARAM_DESCRIPTION)
    if request.query_params.get(PARAM_MONITORING_COMMENTS):
        filters['monitoring_comments__icontains'] = request.query_params.get(PARAM_MONITORING_COMMENTS)
    if request.query_params.get(PARAM_MONITORING_STATUS):
        filters['monitoring_status__icontains'] = request.query_params.get(PARAM_MONITORING_STATUS)
    if request.query_params.get(PARAM_PRODUCT):
        filters['product__icontains'] = request.query_params.get(PARAM_PRODUCT)
    if request.query_params.get(PARAM_PROVIDER):
        filters['provider__icontains'] = request.query_params.get(PARAM_PROVIDER)
    if request.query_params.get(PARAM_TRANSACTION_DATE):
        # this is a date field and should be handled differently
        filters['transaction_date__icontains'] = request.query_params.get(PARAM_TRANSACTION_DATE)
    if request.query_params.get(PARAM_TRANSACTION_TYPE):
        filters['transaction_type__icontains'] = request.query_params.get(PARAM_TRANSACTION_TYPE)
    if request.query_params.get(PARAM_TRANSACTION_REFERENCE) :
        filters['transaction_reference__icontains'] = request.query_params.get(PARAM_TRANSACTION_REFERENCE)        
    if request.query_params.get(PARAM_TRANSACTION_PAN):
        filters['response__PAN__icontains'] = request.query_params.get(PARAM_TRANSACTION_PAN)
    if request.query_params.get(PARAM_RRN_TRANSACTION):
        filters['response__rrn__icontains'] = request.query_params.get(PARAM_RRN_TRANSACTION)
    if request.query_params.get(PARAM_MERCHANT_NAME):
        filters['response__merchantName__icontains'] = request.query_params.get(PARAM_MERCHANT_NAME)
    if request.query_params.get(PARAM_MERCHANT_ADDRESS):
        filters['response__merchantAddress__icontains'] = request.query_params.get(PARAM_MERCHANT_ADDRESS)
    if request.query_params.get(PARAM_TERMINAL_ID):
        filters['response__terminalId__icontains'] = request.query_params.get(PARAM_TERMINAL_ID)
    if request.query_params.get(PARAM_MERCHANT_ID):
        filters['response__merchantId__icontains'] = request.query_params.get(PARAM_MERCHANT_ID)
    if request.query_params.get(PARAM_ORIGINAOR_ACCOUNT_NAME):
        filters['response__originatorAccountName__icontains'] = request.query_params.get(PARAM_ORIGINAOR_ACCOUNT_NAME)
    if request.query_params.get(PARAM_ORIGINAOR_ACCOUNT_NUMBER):
        filters['response__originatorAccountNumber__icontains'] = request.query_params.get(PARAM_ORIGINAOR_ACCOUNT_NUMBER)
    if request.query_params.get(PARAM_BENEFICIARY_ACCOUNT_NAME):
        filters['response__beneficiaryAccountName__icontains'] = request.query_params.get(PARAM_BENEFICIARY_ACCOUNT_NAME)
    if request.query_params.get(PARAM_BENEFICIARY_ACCOUNT_NUMBER):
        filters['response__beneficiaryAccountNumber__icontains'] = request.query_params.get(PARAM_BENEFICIARY_ACCOUNT_NUMBER)
    
    return ETFTransaction.objects.filter(**filters).order_by('-transaction_created_at')


def get_suspected_transactions(request):

    if request.query_params.get("rule_id"):
        return ETFTransaction.objects.filter(
            monitoring_comments__icontains=request.query_params.get('rule_id'),
            transaction_created_at__range=[
            request.query_params.get('start_date'),
            request.query_params.get('end_date')
            ]
        ).order_by('-transaction_created_at')
    elif request.query_params.get('product_type'):
        return ETFTransaction.objects.filter(
            ~Q(monitoring_comments=''),
            ~Q(monitoring_comments=None),
            transaction_type__icontains=request.query_params.get('product_type'),
            transaction_created_at__range=[
                request.query_params.get('start_date'),
                request.query_params.get('end_date')
            ]
        ).order_by('-transaction_created_at')
    else:
        return get_transactions(request)