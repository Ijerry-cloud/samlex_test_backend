import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def send_mail(subject, recipient_list, html_message=''):
    # Connect to the SMTP server
    smtp_obj = smtplib.SMTP(os.environ.get('EMAIL_HOST'), os.environ.get('EMAIL_PORT'))
    smtp_obj.starttls()
    smtp_obj.login(os.environ.get('EMAIL_HOST_USER'), os.environ.get('EMAIL_HOST_PASSWORD=Spout!123456'))

    try:
        for recipient in recipient_list:
            smtp_obj.verify(recipient)
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = 'dev@spoutpayment.com'
            msg['To'] = recipient

            # Attach the HTML content
            html_content = MIMEText(html_message, 'html')
            msg.attach(html_content)

            # Send the email
            smtp_obj.sendmail('dev@spoutpayment.com', [recipient], msg.as_string())
            print("Email sent successfully to:", recipient)

    except smtplib.SMTPException as e:
        print("Error sending email:", str(e))

    finally:
        # Close the connection
        smtp_obj.quit()
