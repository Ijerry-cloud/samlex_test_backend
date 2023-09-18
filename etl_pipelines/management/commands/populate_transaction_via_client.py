from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import Count
from etl_pipelines.models import ETFTransaction, LogTable, Rule, EmailLogTable, ETFUser
from pymongo import MongoClient
from datetime import datetime, timedelta, date
import json
import math
from django.db import connection
# from django.core.mail import send_mail
from api.services.send_mail import send_mail
from django.template import loader
from django.conf import settings
import requests
import os

MONGO_CLIENT_URL = 'mongodb://spoutAdmin:Sp545Yn!_347_Ukb@139.162.209.150:23019/vasapp?readPreference=primary&authSource=admin&ssl=false'
# Number of entries to check for the same threshold value
NUM_ENTRIES_TO_CHECK = 4

def convert_mongodb_timestamp(timestamp):
    try:
        return datetime.utcfromtimestamp(int(timestamp)/1000)
    except Exception as e:
        print(e)
        return None

def can_send_mail(rule_instance, threshold_instance):

    today = timezone.localtime(timezone.now()).date()

    # Condition 1: Check if there is no entry in EmailLogTable for today
    if not EmailLogTable.objects.filter(rule=rule_instance, created_on__date=today).exists():
        print('a')
        return True
    else:
        # Get the last threshold.value for the given rule
        last_entry = EmailLogTable.objects.filter(rule=rule_instance).order_by('-created_on').first()
        if last_entry:
            print('b')
            # Condition 2: Check if there is a change in threshold.value
            if last_entry.threshold.value != threshold_instance.value:
                print('c')
                return True

            # Condition 3: Check the last time mail was sent, based on values set for NUM_ENTRIES_TO_CHECK
            time_threshold = datetime.now() - timedelta(minutes=NUM_ENTRIES_TO_CHECK * 30)
            last_n_entries = EmailLogTable.objects.filter(rule=rule_instance, created_on__gte=time_threshold).order_by('-created_on')
            if not last_n_entries:
                print('d')
                return True
        
        print('e')
        return False


class Command(BaseCommand):
    help = 'Extract and save transactions from MongoDB to PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument('--start_date', type=str,
                            help='Start date in YYYY-MM-DD format')
        parser.add_argument('--end_date', type=str,
                            help='End date in YYYY-MM-DD format')

    def handle(self, *args, **options):    
        try:
            start_date = options['start_date']
            end_date = options['end_date']
            today = timezone.localtime(timezone.now()).date()

            if not start_date or not end_date:
                # Set start_date and end_date to today's date if not provided
                
                start_date = datetime(today.year, today.month,
                                    today.day, tzinfo=timezone.utc)
                end_date = start_date + timedelta(days=1)

            else:
                try:
                    start_date = datetime.strptime(
                        start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                    end_date = datetime.strptime(
                        end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                except ValueError:
                    self.stdout.write('Invalid date format')
                    return

            
            client = MongoClient(MONGO_CLIENT_URL)
            db = client['vasapp']
            transactions = db['transactions']

            # Extract and transform transactions from MongoDB
            extracted_data = []
            count = 0
            for transaction in transactions.find({'createdAt': {'$gte': start_date, '$lte': end_date}}):
                data = {
                    "wallet_id": transaction.get("walletId"),
                    "transaction_status": transaction.get("status"),
                    "credit_status": transaction.get("creditStatus"),
                    "user_id": transaction.get("userId", {}).get("$oid") if type(transaction.get("userId")) == type({}) else transaction.get("userId"),
                    "mongo_id": transaction.get("_id", {}).get("$oid") if type(transaction.get("_id")) == type({}) else transaction.get("_id"),
                    "unique_id": transaction.get("uniqueId"),
                    "debit_response": transaction.get("debitResponse")[0] if (type(transaction.get("debitResponse")) == type([]) and len(transaction.get("debitResponse")) >= 1) else dict(),
                    "payment_method": transaction.get("paymentMethod"),
                    "provider_reference": transaction.get("providerReference"),
                    "response": transaction.get("response"),
                    "account_type": transaction.get("accountType"),
                    'reference': transaction.get('reference'),
                    'amount': transaction.get('amount'),
                    'account': transaction.get('account'),
                    'channel': transaction.get('channel'),
                    'reversal': transaction.get('reversal'),
                    'provider': transaction.get('provider'),
                    'product': transaction.get('product'),
                    'description': transaction.get('description'),
                    "transaction_created_at": transaction.get("createdAt"),
                    "transaction_updated_at": transaction.get("updatedAt"),
                }
                extracted_data.append(ETFTransaction(**data))
                count += 1

            # Save extracted data to PostgreSQL
            ETFTransaction.objects.bulk_create(
                extracted_data,
                ignore_conflicts=True,
            )

            
            with connection.cursor() as cursor:
                cursor.execute('CALL start_transaction_analysis();')
                self.stdout.write(self.style.SUCCESS(
                    'Successfully ran transaction analysis'))
        
            template = loader.get_template(f'{settings.BASE_DIR}/etl_pipelines/templates/TransactionAlert/index.html')
            for rule in Rule.objects.filter(active=True):
                suspected_transactions_today = ETFTransaction.objects.filter(
                    monitoring_comments__icontains=rule.id,
                    transaction_type=rule.product_type,
                    transaction_created_at__date=today).count()
                transactions_today = ETFTransaction.objects.filter(
                    transaction_type=rule.product_type,
                    transaction_created_at__date=today).count()
                suspected_percent = 0
                
                if transactions_today:
                    suspected_percent = math.trunc(
                        (suspected_transactions_today / transactions_today) * 100)
                    # Find threshold value where violation fall under
                    threshold = rule.threshold_set.filter(value__lte=suspected_percent).order_by(
                        '-value').first()  # threshold should have distinct values
                    
                    if threshold:
                        # if can_send_mail(rule, threshold):
                        if True:
                            receipients = threshold.thresholdemails_set.all()
                            receipients_emails = [
                                receipient.user.email for receipient in receipients]
                            print(
                                'found suspicious transactions',
                                suspected_transactions_today,
                                transactions_today,
                                rule,
                                rule.id,
                                suspected_percent,
                                threshold.level
                            )

                            # try and get the merchants that have violated
                            # this transaction the most today
                            transactions = ETFTransaction.objects.filter(
                                transaction_created_at__date=today,
                                monitoring_comments__contains=str(rule.id)
                            ).values('wallet_id').annotate(total_transactions=Count('id')).order_by('-total_transactions')[:10]

                            top_merchant_offenders = []
                            for transaction in transactions:
                                etf_user = ETFUser.objects.filter(data__walletId=transaction.get('wallet_id')).first()
                                top_merchant_offenders.append({
                                    "name": etf_user.get_name() if etf_user else 'N/A', 
                                    "total_transactions": transaction.get('total_transactions')
                                })

                            context = dict()
                            context["rule_description"] = str(rule)
                            context["product"] = rule.product_type.replace("_", " ")
                            context["total_transaction_today"] = transactions_today
                            context["total_flagged_today"] = suspected_transactions_today
                            context["percentage_flagged"] = suspected_percent
                            context["datetime"] = str(today.strftime("%A %d %B, %Y %I:%M%p").replace(" 0", " "))
                            context["threshold_level"] = threshold.level
                            context["top_merchant_offenders"] = top_merchant_offenders
                            html_message = template.render(context)

                            message_type = 'notification'
                            if threshold.level == 'warning':
                                message_type = 'warning'
                            if threshold.level == 'danger':
                                message_type = 'danger'

                            email_data = {
                                "recipient": receipients_emails,
                                "type": message_type,
                                "subject": "Fraudulent Transaction Alert",
                                "message": html_message,
                            }

                            # Send email via API
                            response = requests.post(os.environ.get("EMAIL_API_URL"), json=email_data)
                            now = datetime.now(tz=timezone.get_current_timezone())
                            if response.status_code == 200:
                                # Email sent successfully
                                log_description = f"Sent mail to {', '.join(receipients_emails)}"
                                LogTable.objects.create(error_message=log_description, timestamps=now)
                            else:
                                # Email sending failed
                                log_description = f"Failed to send email. Response: {response.text}"
                                LogTable.objects.create(error_message=log_description, timestamps=now)

                            EmailLogTable.objects.create(
                                rule=rule,
                                threshold=threshold,
                                recipients=','.join(receipients_emails),
                                message=log_description
                            )


            now = datetime.now(tz=timezone.get_current_timezone())
            LogTable.objects.create(
                error_message="Successfully ran transaction analysis",
                timestamps=now
            )
        
        except Exception as e:
            # Save the error description to the email log table
            print('e: ', e)
            log_description = f"Error occurred: {str(e)}"
            now = datetime.now()
            LogTable.objects.create(error_message=log_description, timestamps=now)
