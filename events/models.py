from django.db import models
from django.conf import settings
from django.utils import timezone

def default_event_image():
    return "default-event.jpg"
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="events")
    image = models.ImageField(upload_to="events/", default=default_event_image)
    attendees = models.ManyToManyField(settings.AUTH_USER_MODEL, through="RSVP", related_name="rsvp_events", blank=True)
    

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        return f"{self.name} ({self.date})"


class RSVP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rsvps")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="rsvps")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("user", "event")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.event.name}"