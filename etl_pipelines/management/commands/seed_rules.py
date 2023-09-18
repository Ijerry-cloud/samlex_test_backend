from django.db import transaction
from etl_pipelines.models import Rule, Product
from django.core.management.base import BaseCommand
from etl_pipelines.conditions import *


TRANSFER_RULES = [
   {
    "description": "EXCEEEDED DAILY TRANSFER LIMIT",
    "product": "TRANSFER",
    "condition": "exceeded daily limit",
    "value": 5000000
   },
   {
    "description": "EXCEDEDED SINGLE TRANSFER LIMIT",
    "product": "TRANSFER",
    "condition": "exceeded single transaction limit",
    "value": 500000
   },
   {
    "description": "FLAG DUPLICATE",
    "product": "TRANSFER",
    "condition": "flag duplicate transaction",
    "value": 3
   },
    {
    "description": "EXCEEDED TRANSFER LIMIT",
    "product": "TRANSFER",
    "condition": "exceeded limit",
    "value": 500000
   },
   {
    "description": "EXCEEDED WALLET BALANCE",
    "product": "TRANSFER",
    "condition": "exceeded balance",
    "value": 500000
   }
]


WITHDRAWAL_RULES = [
    {
    "description": "EXCEEDED DAILY WITHDRAWAL LIMIT",
    "product": "WITHDRAWAL",
    "condition": "exceeded daily limit",
    "value": 500000
   },
   {
    "description": "EXCEEDED MAXIMUM NUMBER OF DAILY WITHDRAWAL ON CARD",
    "product": "WITHDRAWAL",
    "condition": "exceeded number of daily transaction on card",
    "value": 3
   },
]

VALUE_ADDED_SERVICES = [
    {
        "description": "EXCEEDED DAILY TRANSACTION LIMIT",
        "product": "AIRTIME_VTU",
        "condition": "exceeded daily limit",
        "value": 100000
   },
   {
        "description": "EXCEEDED DAILY TRANSACTION LIMIT",
        "product": "DATA_RECHARGE",
        "condition": "exceeded daily limit",
        "value": 100000
   },
   {
        "description": "EXCEEDED SINGLE TRANSACTION LIMIT",
        "product": "AIRTIME_VTU",
        "condition": "exceeded single transaction limit",
        "value": 10000
   },
   {
        "description": "EXCEEDED SINGLE TRANSACTION LIMIT",
        "product": "DATA_RECHARGE",
        "condition": "exceeded single transaction limit",
        "value": 30000
   },
   {
        "description": "FLAG DUPLICATE",
        "product": "AIRTIME_VTU",
        "condition": "flag duplicate transaction",
        "value": 3
   },
   {
        "description": "FLAG DUPLICATE",
        "product": "DATA_RECHARGE",
        "condition": "flag duplicate transaction",
        "value": 3
   }
]

class Command(BaseCommand):
    """
    Management command to seed the DB with initial rules
    """

    help = "Populate the rules table with initial rules"

    @transaction.atomic
    def handle(self, *args, **kwargs):

        if Product.objects.count() == 0:
            print('no products in the database, please seed the database')
            sys.exit(1)

        ALL_RULES = [*TRANSFER_RULES, *WITHDRAWAL_RULES, *VALUE_ADDED_SERVICES]
        for rule in ALL_RULES:
            Rule.objects.create(
                description=rule.get("description"),
                product_type=rule.get("product"),
                condition=rule.get("condition"),
                value=rule.get("value")
            )

        print('rules seeded successfully')