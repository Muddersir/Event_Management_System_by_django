from django import forms
from .models import Event, Participant, Category

class DateInput(forms.DateInput):
    input_type = "date"

class TimeInput(forms.TimeInput):
    input_type = "time"

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "description", "date", "time", "location", "category", "participants"]
        widgets = {
            "date": DateInput(),
            "time": TimeInput(),
            "participants": forms.CheckboxSelectMultiple(),
        }

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["name", "email"]

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]