from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from etl_pipelines.models import LogTable, EmailLogTable, ETFUser, ETFTransaction, MerchantMetric, MerchantMetricEmail, MerchantMetricEmailLog
from pymongo import MongoClient
from datetime import datetime, timedelta, date
import json
from django.db import connection
from api.services.send_mail import send_mail
from django.template import loader
from django.conf import settings
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from django.utils.safestring import mark_safe
import locale
import requests
import os


from decimal import Decimal, ROUND_HALF_UP

MONGO_CLIENT_URL = 'mongodb://spoutAdmin:Sp545Yn!_347_Ukb@139.162.209.150:23019/vasapp?readPreference=primary&authSource=admin&ssl=false'

def monitor_merchant_transaction_spikes(N_DAYS, N_DIFFERENTIAL, MINIMUM_AMOUNT):
    
    today = timezone.localtime(timezone.now()).date()

    # Get walletIds with transactions carried out today
    wallet_ids_today = ETFTransaction.objects.filter(transaction_created_at__date=today).values_list('wallet_id', flat=True).distinct()

    # Create dictionaries to store exceeded count and amount
    exceeded_count_dict = {}
    exceeded_amount_dict = {}

    for wallet_id in wallet_ids_today:
        # Get total count and total amount for the last N_DAYS excluding today
        yesterday = today - timedelta(days=1)

        # Set end_date to yesterday's date
        end_date = yesterday
        start_date = end_date - timedelta(days=N_DAYS-1)
        

        wallet_transactions = ETFTransaction.objects.filter(
            wallet_id=wallet_id,
            transaction_created_at__date__range=(start_date, end_date)
        )


        total_count_last_n_days = wallet_transactions.count()
        total_amount_last_n_days = wallet_transactions.aggregate(total_amount=Sum('amount'))['total_amount'] or 0

        # Calculate average count and average amount
        average_count = Decimal(total_count_last_n_days / N_DAYS).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        average_amount = Decimal(total_amount_last_n_days / N_DAYS).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

        # Get count and total amount for today
        today_transactions = ETFTransaction.objects.filter(wallet_id=wallet_id, transaction_created_at__date=today)
        count_today = today_transactions.count()
        total_amount_today = Decimal(today_transactions.aggregate(total_amount=Sum('amount'))['total_amount'] or 0).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

        # Calculate the difference in percentage
        difference_count = ((count_today - average_count) / average_count) * 100 if average_count !=  0 else 0 # do this to avoid zero division error
        difference_amount = ((total_amount_today - average_amount) / average_amount) * 100 if average_amount != 0 else 0

        # Check if the difference exceeds the N_DIFFERENTIAL
        if difference_count > N_DIFFERENTIAL:
            # print('##################################')
            # print(f'wallet id: {wallet_id}')
            # print(f'today count: {count_today}')
            # print(f'today amount: {total_amount_today}')
            # print(f'average count: {average_count}')
            # print(f'average amount: {average_amount}')
            # print(f'difference count: {difference_count}')
            # print(f'difference amount: {difference_amount}')
            # print('################################')
            # print(count_today, average_count, difference_count, difference_amount)
            exceeded_count_dict[wallet_id] = {
                "difference_count": Decimal(difference_count).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
                "wallet_id": wallet_id,
                "today_count": Decimal(count_today).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
                "today_amount": Decimal(total_amount_today).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
                "average_count": Decimal(average_count).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
                "average_amount": Decimal(average_amount).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
                "difference_count": Decimal(difference_count).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
                "difference_amount": Decimal(difference_amount).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
            }


        if  total_amount_today > MINIMUM_AMOUNT and difference_amount > N_DIFFERENTIAL:
            # print('##################################')
            # print(f'wallet id: {wallet_id}')
            # print(f'today count: {count_today}')
            # print(f'today amount: {total_amount_today}')
            # print(f'average count: {average_count}')
            # print(f'average amount: {average_amount}')
            # print(f'difference count: {difference_count}')
            # print(f'difference amount: {difference_amount}')
            # print('################################')
            # print(count_today, average_count, difference_count, difference_amount)
            exceeded_amount_dict[wallet_id] = {
                "difference_count": Decimal(difference_count).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
                "wallet_id": wallet_id,
                "today_count": Decimal(count_today).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
                "today_amount": Decimal(total_amount_today).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
                "average_count": Decimal(average_count).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
                "average_amount": Decimal(average_amount).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
                "difference_count": Decimal(difference_count).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
                "difference_amount": Decimal(difference_amount).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP),
            }
        
    return exceeded_count_dict, exceeded_amount_dict


class Command(BaseCommand):
    help = 'Extract and save users from MongoDB to PostgreSQL'

    def handle(self, *args, **options):
        try:
            N_DAYS = 0
            N_DIFFERENTIAL = 0

            # Connect to MongoDB
            client = MongoClient(MONGO_CLIENT_URL)
            db = client['vasapp']
            etf_users = db['users']

            # Extract and transform transactions from MongoDB
            extracted_data = []
            merchant_reference = dict()
            for etf_user in etf_users.find({}):
                mongo_id = etf_user.get("_id")

                temp_dict = dict()
                # remove any sensitive information
                for key in etf_user.keys():
                    if key in ["_id", "password", "pin", "resetPin", "createdAt", "updatedAt"]:
                        continue
                    if isinstance(etf_user.get(key), datetime):
                        continue
                    temp_dict[key] = etf_user.get(key)

                data = {
                    "mongo_id": mongo_id,
                    "data": temp_dict,
                }
                name = etf_user.get("businessName") if etf_user.get("businessName") else (
                        etf_user.get("username") if etf_user.get("username") else
                        f'{etf_user.get("firstName")} {etf_user.get("lastName")}')
                merchant_reference[etf_user.get("walletId")] = name
                extracted_data.append(ETFUser(**data))

            # Save extracted data to PostgreSQL
            ETFUser.objects.bulk_create(
                extracted_data,
                ignore_conflicts=True,
            )

            # Record successful analysis in LogTable
            now = datetime.now()
            LogTable.objects.create(
                error_message="Successfully ran merchant analysis",
                timestamps=now
            )

            # Fetch all MerchantMetricEmail objects
            merchant_metric_emails = MerchantMetricEmail.objects.select_related('user').all()

            merchant_metric = MerchantMetric.objects.filter(name="merchant_monitoring_metrics").first()

            # Get the latest MerchantMetricEmailLog record
            latest_log = MerchantMetricEmailLog.objects.order_by('-created_on').first()

            if merchant_metric:
                N_DAYS = merchant_metric.no_of_days
                N_DIFFERENTIAL = merchant_metric.percentage_violation
                minimum_amount = merchant_metric.minimum_amount
                sending_intervals = merchant_metric.sending_intervals

            # Check if the sending interval has passed since the last email sent
            if latest_log and (timezone.now() - latest_log.created_on) < timedelta(hours=sending_intervals):
                self.stdout.write("Sending interval not reached. Skipping email sending.")
                # return

            exceeded_count_dict, exceeded_amount_dict = monitor_merchant_transaction_spikes(N_DAYS,
                                                                                            N_DIFFERENTIAL,
                                                                                            minimum_amount)
            
            # Sort the exceeded amount dictionary by difference_amount in descending order
            sorted_amount_dict = sorted(exceeded_amount_dict.items(), key=lambda x: x[1]['difference_amount'],
                                        reverse=True)
            # print(sorted_amount_dict)
            amount_list = []
            for wallet_id , wallet_data in sorted_amount_dict:
                amount_list.append(
                    {
                        "date": f"{str(timezone.localtime(timezone.now()).date())}",
                        "name": f"{merchant_reference.get(wallet_id)}",
                        "rule": "Average Transaction Amount",
                        "average_amount": format(wallet_data.get("average_amount"), ","),
                        "total_amount_today": format(wallet_data.get("today_amount"), ","),
                        "percentage_spike": format(wallet_data.get("difference_amount"), ",")
                    }
                )

            # Build the list for exceeded amount
            # for wallet_id, wallet_data in sorted_amount_dict:
            #     amount_text = 'spike'
            #     color_code = 'green' if wallet_data.get("difference_amount") < 0 else 'red'
            #     if wallet_data.get("difference_amount") < 0:
            #         amount_text = 'dip'

            #     average_amount = format(wallet_data.get("average_amount"), ",")
            #     today_amount = format(wallet_data.get("today_amount"), ",")
            #     difference_amount = format(wallet_data.get("difference_amount"), ",")

            #     amount_item = f"In the past {N_DAYS} days, {merchant_reference.get(wallet_id)} has maintained an average transaction amount of {average_amount}. Today ({str(timezone.localtime(timezone.now()).date())}), a transaction of {today_amount} was recorded. This indicates a {difference_amount}% {amount_text} compared to the average amount."
            #     amount_list.append({'text': amount_item, 'color': color_code})
            # amount_html = '<ul>'
            # for item in amount_list:
            #     amount_html += f'<li style="color: {item["color"]}">{item["text"]}</li>'
            # amount_html += '</ul>'

            template = loader.get_template('MerchantAlert/index.html')
            context = {
                'amount_list': amount_list,
                "no_of_days": N_DAYS
            }
            html_message = template.render(context)
            
            recipient_emails = [email.user.email for email in merchant_metric_emails]
            if amount_list:
                # Send email with the alert
                # res = send_mail(
                #     "Merchant Monitoring Alert",
                #     recipient_emails,
                #     html_message
                # )
                # Prepare email data
                email_data = {
                    "recipient": recipient_emails,
                    "type": "notification",
                    "subject": "Merchant Monitoring Alert",
                    "message": html_message,
                }

                # Send email via API
                response = requests.post(os.environ.get("EMAIL_API_URL"), json=email_data)
                if response.status_code == 200:
                    # Email sent successfully
                    log_description = f"Sent mail to {', '.join(recipient_emails)}"
                    MerchantMetricEmailLog.objects.create(description=log_description)
                else:
                    # Email sending failed
                    log_description = f"Failed to send email. Response: {response.text}"
                    MerchantMetricEmailLog.objects.create(description=log_description)

        except Exception as e:
            # Save the error description to the email log table
            print('e: ', e)
            log_description = f"Error occurred: {str(e)}"
            MerchantMetricEmailLog.objects.create(description=log_description)