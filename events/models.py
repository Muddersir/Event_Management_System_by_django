from django.db import models

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
    participants = models.ManyToManyField("Participant", related_name="events", blank=True)

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        return f"{self.name} ({self.date})"


class Participant(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    # events relationship defined in Event.participants M2M

    def __str__(self):
        return f"{self.name} <{self.email}>"