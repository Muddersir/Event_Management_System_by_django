from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    # Events - list & detail (class-based)
    path("", views.EventListView.as_view(), name="event_list"),
    path("create/", views.EventCreateView.as_view(), name="event_create"),
    path("<int:pk>/", views.EventDetailView.as_view(), name="event_detail"),
    path("<int:pk>/edit/", views.EventUpdateView.as_view(), name="event_update"),
    path("<int:pk>/delete/", views.EventDeleteView.as_view(), name="event_delete"),

    # Participants CRUD (admin-managed users)
    path("participants/", views.ParticipantListView.as_view(), name="participant_list"),
    path("participants/create/", views.ParticipantCreateView.as_view(), name="participant_create"),
    path("participants/<int:pk>/edit/", views.ParticipantUpdateView.as_view(), name="participant_update"),
    path("participants/<int:pk>/delete/", views.ParticipantDeleteView.as_view(), name="participant_delete"),

    # Categories CRUD
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/create/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),

    # RSVP
    path("<int:pk>/rsvp/", views.rsvp_view, name="event_rsvp"),
    path("my-rsvps/", views.my_rsvps, name="my_rsvps"),

    # Dashboards
    path("dashboard/admin/", views.admin_dashboard, name="dashboard_admin"),
    path("dashboard/organizer/", views.organizer_dashboard, name="dashboard_organizer"),
    path("dashboard/participant/", views.participant_dashboard, name="dashboard_participant"),
]