from django.db import transaction
from etl_pipelines.models import Product
from django.core.management.base import BaseCommand



SPOUT_PRODUCTS = [
    {
        "name": "9mobilevtu",
        "type": "AIRTIME_VTU"
    },
    {
        "name": "airtelvtu",
        "type": "AIRTIME_VTU"
    },
    {
        "name": "glovtu",
        "type": "AIRTIME_VTU"
    },
    {
        "name": "mtnvtu",
        "type": "AIRTIME_VTU"
    },
    {
        "name": "transfer",
        "type": "TRANSFER"
    },
    {
        "name": "withdrawal",
        "type": "WITHDRAWAL"
    },
    {
        "type": "CABLE_RECHARGE",
        "name": "multichoice"
    },
    {
        "type": "CABLE_RECHARGE",
        "name": "startimes"
    },
    {
        "type": "CABLE_RECHARGE",
        "name": "cgate"
    },
    {
        "type": "CABLE_RECHARGE",
        "name": "mcash"
    },
    {
        "type": "DATA_RECHARGE",
        "name": "mtndata"
    },
    {
        "type": "DATA_RECHARGE",
        "name": "glodata"
    },
    {
        "type": "DATA_RECHARGE",
        "name": "airteldata"
    },
    {
        "type": "DATA_RECHARGE",
        "name": "smile"
    },
    {
        "type": "DATA_RECHARGE",
        "name": "9mobiledata"
    },
    {
        "type": "ELECTRICITY_RECHARGE",
        "name": "ekedc"
    },
    {
        "type": "ELECTRICITY_RECHARGE",
        "name": "ikedc"
    },
    {
        "type": "ELECTRICITY_RECHARGE",
        "name": "ibedc"
    },
    {
        "type": "ELECTRICITY_RECHARGE",
        "name": "eedc"
    },
    {
        "type": "ELECTRICITY_RECHARGE",
        "name": "kedco"
    },
    {
        "type": "ELECTRICITY_RECHARGE",
        "name": "phedc"
    },
    {
        "type": "ELECTRICITY_RECHARGE",
        "name": "aedc"
    },
    {
        "type": "ELECTRICITY_RECHARGE",
        "name": "kadec"
    },
    {
        "type": "ELECTRICITY_RECHARGE",
        "name": "jedc"
    }
]


class Command(BaseCommand):
    """
    Management command to seed the DB with products
    """

    help = "Populate the products table with predefined product list for spout pay"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        for product in SPOUT_PRODUCTS:
            Product.objects.create(
                product_name=product.get("name"),
                product_type=product.get("type")
            )