from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    # Include events urls under /events/ with the 'events' namespace
    path("events/", include("events.urls", namespace="events")),
    # Redirect root URL to the events list (avoids including the same URLconf twice and duplicate namespace)
    path("", RedirectView.as_view(pattern_name="events:event_list", permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)