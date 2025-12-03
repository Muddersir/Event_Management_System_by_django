from django import forms
from .models import Event
from django.forms import DateInput, TimeInput

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "description", "date", "time", "location", "category", "image"]
        widgets = {
            "date": DateInput(attrs={"type": "date"}),
            "time": TimeInput(attrs={"type": "time"}),
        }
