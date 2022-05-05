from email.mime.text import MIMEText
import smtplib
import os
from email.mime.multipart import MIMEMultipart


def send_email(email):
    text = 'Hello! I rewrite this code. I don`t know how, but now it works!!! You can congratulate me!!!!'
    address = os.getenv("FROM")
    password = os.getenv("PASSWORD")
    msg = MIMEMultipart()
    msg['From'] = address
    msg['To'] = email
    msg['Subject'] = 'Welcome to our network!'
    msg.attach(MIMEText(text, 'plain'))

    server = smtplib.SMTP_SSL(os.getenv("HOST"), os.getenv("PORT"))
    print('connect', address, password)
    server.login(address, password)
    print('login')

    server.send_message(msg)
    server.quit()
    return True