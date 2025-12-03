from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    """
    Send account activation email to newly created users who are inactive.
    Triggered on User creation. Uses default_token_generator.
    """
    if created and not instance.is_active:
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        token = default_token_generator.make_token(instance)
        subject = "Activate your account"
        message = render_to_string("accounts/activation_email.html", {
            "user": instance,
            "uid": uid,
            "token": token,
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email], fail_silently=False)