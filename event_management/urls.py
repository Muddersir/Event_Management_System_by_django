from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("events/", include("events.urls", namespace="events")),
    path("", include("events.urls", namespace="events")),  # root to events
]
