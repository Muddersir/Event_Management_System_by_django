from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard-data/", views.dashboard_data, name="dashboard_data"),

    # Events CRUD
    path("", views.EventListView.as_view(), name="event_list"),
    path("events/create/", views.EventCreateView.as_view(), name="event_create"),
    path("events/<int:pk>/", views.EventDetailView.as_view(), name="event_detail"),
    path("events/<int:pk>/edit/", views.EventUpdateView.as_view(), name="event_update"),
    path("events/<int:pk>/delete/", views.EventDeleteView.as_view(), name="event_delete"),

    # Participants CRUD
    path("participants/", views.ParticipantListView.as_view(), name="participant_list"),
    path("participants/create/", views.ParticipantCreateView.as_view(), name="participant_create"),
    path("participants/<int:pk>/edit/", views.ParticipantUpdateView.as_view(), name="participant_update"),
    path("participants/<int:pk>/delete/", views.ParticipantDeleteView.as_view(), name="participant_delete"),

    # Categories CRUD
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/create/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
]