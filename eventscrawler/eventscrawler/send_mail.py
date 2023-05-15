from datetime import datetime, timedelta
from email.message import EmailMessage
import ssl
import smtplib


def send_email(content):
    email_sender = 'robertcristy20@gmail.com'
    email_password = 'vqnsgvttsmmuxfpe'
    email_receiver = 'clau_nik@yahoo.com'
    subject = 'Future events'
    body = f"There will be a conference at the date: {content}"

    email = EmailMessage()
    email['From'] = email_sender
    email['To'] = email_receiver
    email['Subject'] = subject
    email.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, email.as_string())


today = datetime.today()
date_str = str("Wednesday, April 19, 2023")
date_format = str('%A %B %d %Y')

date_str = date_str.replace(",", "")

date_str = datetime.strptime(date_str, date_format)

if date_str <= today + timedelta(30):
    print("Send mail!!")
    send_email(date_str)
else:
    print("Dont send mail!!")



