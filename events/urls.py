from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("", views.EventListView.as_view(), name="event_list"),
    path("create/", views.EventCreateView.as_view(), name="event_create"),
    path("<int:pk>/", views.EventDetailView.as_view(), name="event_detail"),
    path("<int:pk>/edit/", views.EventUpdateView.as_view(), name="event_update"),
    path("<int:pk>/delete/", views.EventDeleteView.as_view(), name="event_delete"),

    path("participants/", views.AdminDashboardView.as_view(), name="participants_placeholder"),

    # Categories
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/create/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),

    # RSVP
    path("<int:pk>/rsvp/", views.RSVPView.as_view(), name="event_rsvp"),
    path("my-rsvps/", views.MyRSVPsView.as_view(), name="my_rsvps"),

    # dashboards
    path("dashboard/admin/", views.AdminDashboardView.as_view(), name="dashboard_admin"),
    path("dashboard/organizer/", views.OrganizerDashboardView.as_view(), name="dashboard_organizer"),
    path("dashboard/participant/", views.ParticipantDashboardView.as_view(), name="dashboard_participant"),
]