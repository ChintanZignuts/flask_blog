from flask_mail import Message
from app.extensions import mail

def send_email(to_email, subject, body):
    """ Sends an email using Mailtrap """
    msg = Message(subject, recipients=[to_email], body=body)
    mail.send(msg)