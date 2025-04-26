
from celery import shared_task
from django.core.mail import EmailMessage

@shared_task
def send_activation_email(subject, message, recipient_list, from_email=None):
    """
    Sends an email asynchronously.
    """
    email = EmailMessage(subject, message, from_email=from_email, to=recipient_list)
    email.send(fail_silently=False)
