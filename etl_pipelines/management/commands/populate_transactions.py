from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from etl_pipelines.models import ETFTransaction
import json
from django.db import connection

file_path = '/Users/jerry/Desktop/projects/django 3-2 projects/etop-reporting-backend/etl_pipelines/management/commands/transactionsZ.json'

def convert_mongodb_timestamp(timestamp):
    try:
        return datetime.utcfromtimestamp(int(timestamp)/1000)
    except Exception as e:
        print(e)
        return None

def transform_transaction(data):
    """
        ############# TRANSACTION SAMPLE FOR WITDRAWAL ###############

            {
                "_id": {
                    "$oid": "63a75d43f620f8ad845b3a4d"
                },
                "reversal": false,
                "creditStatus": true,
                "uniqueId": "N/A",
                "status": "successful",
                "debitResponse": [],
                "product": "withdrawal",
                "reference": "1671913580462SPL00062022122481250",
                "amount": 2000,
                "response": {
                    "responseCode": "00",
                    "description": "Approved",
                    "MTI": "0200",
                    "amount": 2000,
                    "terminalId": "2SPL0006",
                    "responseDescription": "Approved",
                    "PAN": "506109XXXXXXXX7770",
                    "STAN": "077288",
                    "authCode": "637459",
                    "transactionTime": "2022-12-24 20:12:50",
                    "reversal": false,
                    "merchantId": "2302BA000009611",
                    "merchantName": "SPOUT PAYMENT INTERNAT",
                    "merchantAddress": "ONAL LIMITED     ",
                    "rrn": "167191358046",
                    "channel": "linuxpos"
                },
                "userId": {
                    "$oid": "6399d5abb8549fea4c63df92"
                },
                "walletId": "107371894",
                "account": "N/A",
                "paymentMethod": "card",
                "channel": "linuxpos",
                "provider": "tms",
                "packages": [],
                "createdAt": {
                    "$date": {
                    "$numberLong": "1671912771751"
                    }
                },
                "updatedAt": {
                    "$date": {
                    "$numberLong": "1671912771751"
                    }
                },
                "__v": 0
                }

        ##############################################################

        ############ TRANSACTION SAMPLE FOR TRANSFER  ################

            {
                "_id": {
                "$oid": "63aeebd0f620f8ad845b3e7a"
                },
                "reversal": false,
                "creditStatus": false,
                "uniqueId": "0123456789139214643387996",
                "status": "successful",
                "debitResponse": [
                {
                    "error": false,
                    "message": "Wallet Debited Successfully",
                    "debitAmount": 110
                }
                ],
                "userId": {
                "$oid": "63432ba2a3095d872ea25d50"
                },
                "walletId": "108801733",
                "product": "transfer",
                "amount": 100,
                "account": "0112345678",
                "channel": "androidpos",
                "provider": "nibss",
                "reference": "VASTRA1088017331672408016842",
                "productCode": "",
                "packages": [],
                "createdAt": {
                "$date": {
                    "$numberLong": "1672408016842"
                }
                },
                "updatedAt": {
                "$date": {
                    "$numberLong": "1672408016842"
                }
                },
                "__v": 1,
                "paymentMethod": "cash",
                "description": "Transaction Successful",
                "providerReference": "NIPMINI/000076221230134709895159273563/VASTRA1088017331672408016842",
                "response": {
                "responseCode": "00",
                "sessionID": "999999221230144709121938819163",
                "transactionId": "000076221230134709895159273563",
                "channelCode": 1,
                "nameEnquiryRef": "999999221230144709121938819163",
                "destinationInstitutionCode": "999998",
                "beneficiaryAccountName": "vee Test",
                "beneficiaryAccountNumber": "0112345678",
                "beneficiaryKYCLevel": "1",
                "beneficiaryBankVerificationNumber": "33333333332",
                "originatorAccountName": "Test Sender",
                "originatorAccountNumber": "0112345678",
                "originatorBankVerificationNumber": "33333333333",
                "originatorKYCLevel": "1",
                "transactionLocation": "1.38716,3.05117",
                "narration": "Transfer from Test Sender",
                "paymentReference": "NIPMINI/000076221230134709895159273563/VASTRA1088017331672408016842",
                "amount": 100
                }
            }            

        ##############################################################

        ###### TRANSACTION SAMPLE FOR VAS (VALUE ADDED SERVICE) ######

            {
                "_id": {
                "$oid": "63a72477f620f8ad845b3a30"
                },
                "reversal": false,
                "creditStatus": false,
                "uniqueId": "9822090270834925619182882516",
                "status": "successful",
                "debitResponse": [
                {
                    "error": false,
                    "message": "Wallet Debited Successfully",
                    "debitAmount": 2800
                }
                ],
                "userId": {
                "$oid": "6385ede9e7a369877c32cdee"
                },
                "walletId": "164738994",
                "product": "multichoice",
                "amount": 2800,
                "account": "7018819293",
                "accountType": "gotv",
                "channel": "mobile",
                "provider": "capricorn",
                "reference": "VASMUL1647389941671898231541",
                "packages": [],
                "createdAt": {
                "$date": {
                    "$numberLong": "1671898231541"
                }
                },
                "updatedAt": {
                "$date": {
                    "$numberLong": "1671898231541"
                }
                }

        ###############################################################

    """
    result = dict()
    # pop these keys 
    result = {
        **data,
        "wallet_id": data.get("walletId"),
        "transaction_status": data.get("status"),
        "credit_status": data.get("creditStatus"),
        "user_id": data.get("userId",{}).get("$oid"),
        "mongo_id": data.get("_id", {}).get("$oid"),
        "unique_id": data.get("uniqueId"),
        "debit_response": data.get("debitResponse")[0] if ( type(data.get("debitResponse")) == type ([]) and len(data.get("debitResponse")) >= 1 ) else dict(),
        "payment_method": data.get("paymentMethod"),
        "provider_reference": data.get("providerReference"),
        "response": data.get("response"),
        "account_type": data.get("accountType"),
        "transaction_created_at": convert_mongodb_timestamp(data.get("createdAt").get("$date").get("$numberLong")),
        "transaction_updated_at": convert_mongodb_timestamp(data.get("updatedAt").get("$date").get("$numberLong")),
    }
    keys_to_remove = [
        "_id", "creditStatus", "uniqueId", "debitResponse", "userId", "walletId", "paymentMethod",
        "packages", "createdAt", "updatedAt", "__v", "status", "accountType", "providerReference",
        "productCode", "validationResponse", "creditResponse"
    ]
    for key in keys_to_remove:
        result.pop(key, None)
    return result

class Command(BaseCommand):
    """
    Management Command for populating db with sample transactions
    """

    help = "Populate ETF Transaction table with sample data"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        f = open(file_path)
        data  = json.loads(f.read())

        # print(data)
        transactions_list = list()
        for d in data:
            
            transactions_list.append(transform_transaction(d))

        ETFTransaction.objects.bulk_create(
            map(lambda txn: ETFTransaction(**txn), transactions_list),
            ignore_conflicts=True,
            )
        
        f.close()

        with connection.cursor() as cursor:
            cursor.execute('CALL start_transaction_analysis();')