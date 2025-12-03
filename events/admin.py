from django.contrib import admin
from .models import Event, Category, RSVP

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "time", "location", "category")
    list_filter = ("category", "date")
    search_fields = ("name", "location")

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "created_at")
    search_fields = ("user__username", "event__name")