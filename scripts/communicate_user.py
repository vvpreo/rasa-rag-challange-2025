#! .venv/bin/python
import os

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

send_from = 'motoexpertai@gmail.com'
email_pass = os.environ.get('EMAIL_PASS')


def send_email(to_email: str, body: str, subject="Conversation summary with Moto Expert AI"):
    gmail_user = send_from
    gmail_password = email_pass

    # Create message
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach body text
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, to_email, text)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
    else:
        print("Email sent successfully!")


if __name__ == '__main__':
    send_email(to_email="vvpreo@gmail.com", body="This is a test email sent from Python!")
