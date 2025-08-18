# auth/utils.py
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import render_template
from wsgi import app, mail

def get_serializer():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])

def generate_token(data):
    s = get_serializer()
    return s.dumps(data, salt='email-confirm')

def verify_token(token, max_age=3600):
    s = get_serializer()
    try:
        return s.loads(token, salt='email-confirm', max_age=max_age)
    except:
        return None

def send_email(to, subject, template, **kwargs):
    msg = Message(
        subject,
        recipients=[to],
        sender=app.config['MAIL_DEFAULT_SENDER'],
        html=render_template(template, **kwargs)
    )
    mail.send(msg)