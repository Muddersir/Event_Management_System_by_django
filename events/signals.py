from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RSVP
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=RSVP)
def send_rsvp_notification(sender, instance, created, **kwargs):
    """
    When a user RSVPs to an event:
    - Send a confirmation email to the user
    - Notify event organizers (users in Organizer group) about the new RSVP (simple implementation: send to all organizers)
    """
    if not created:
        return

    user = instance.user
    event = instance.event

    # Confirmation to user
    subject_user = f"RSVP confirmed: {event.name}"
    message_user = render_to_string("events/emails/rsvp_confirm_email.txt", {"user": user, "event": event})
    send_mail(subject_user, message_user, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)

    # Notify organizers (all users in Organizer group)
    from django.contrib.auth.models import Group
    organizers = Group.objects.filter(name="Organizer").first()
    if organizers:
        organizer_emails = [u.email for u in organizers.user_set.all() if u.email]
        if organizer_emails:
            subject_org = f"New RSVP for {event.name}"
            message_org = render_to_string("events/emails/rsvp_notify_organizers.txt", {"user": user, "event": event})
            send_mail(subject_org, message_org, settings.DEFAULT_FROM_EMAIL, organizer_emails, fail_silently=True)