from django.db.models.functions import Concat, Cast
from django.db.models import Value, CharField, JSONField
from django.db.models.functions import Coalesce
from etl_pipelines.models import ETFUser


def get_merchants_list():

    merchants_data = ETFUser.objects.filter(data__isActive=True)

    
    merchants_list = []
    for merchant in merchants_data:
        temp_data = dict()
        temp_data["wallet_id"] = merchant.data.get("walletId")
        temp_data["mongo_id"] = merchant.mongo_id
        temp_data["merchant_name"] = merchant.get_name()
        temp_data["businessName"] = merchant.get_name()
        merchants_list.append(temp_data)

    ordered_merchants = sorted(merchants_list, key=lambda x: x["merchant_name"])

    return { "data": ordered_merchants, "count": len(merchants_list) }
