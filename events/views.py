from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.utils import timezone

from .models import Event, Category, RSVP
from .forms import EventForm

User = get_user_model()

# Role helper and decorator
def role_required(*group_names):
    """
    Decorator factory: allow access only to users in any of the given groups or superusers.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            user_groups = request.user.groups.values_list("name", flat=True)
            if any(g in group_names for g in user_groups):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You do not have permission to access this page.")
        return _wrapped_view
    return decorator


# -------------------------
# Events: List / Detail / CRUD
# -------------------------
class EventListView(generic.ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 20

    def get_queryset(self):
        qs = Event.objects.select_related("category").prefetch_related("rsvps__user")
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "")
        start_date = self.request.GET.get("start_date", "")
        end_date = self.request.GET.get("end_date", "")

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(location__icontains=q))

        if category:
            qs = qs.filter(category__id=category)

        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)

        qs = qs.annotate(participant_count=Count("attendees", distinct=True))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_unique_participants"] = User.objects.filter(rsvps__isnull=False).distinct().count()
        ctx["categories"] = Category.objects.all()
        ctx["q"] = self.request.GET.get("q", "")
        ctx["selected_category"] = self.request.GET.get("category", "")
        ctx["start_date"] = self.request.GET.get("start_date", "")
        ctx["end_date"] = self.request.GET.get("end_date", "")
        return ctx


class EventDetailView(generic.DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.select_related("category").prefetch_related("rsvps__user")


@method_decorator(role_required("Organizer", "Admin"), name="dispatch")
class EventCreateView(generic.CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")


@method_decorator(role_required("Organizer", "Admin"), name="dispatch")
class EventUpdateView(generic.UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")


@method_decorator(role_required("Organizer", "Admin"), name="dispatch")
class EventDeleteView(generic.DeleteView):
    model = Event
    template_name = "events/event_delete.html"
    success_url = reverse_lazy("events:event_list")


# -------------------------
# Participant CRUD (manage users in Participant group)
# Admin-only pages to manage Participant users.
# These views are provided so urls referencing participant_* exist and work.
# -------------------------
class ParticipantCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")


class ParticipantUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "is_active")


@method_decorator(role_required("Admin"), name="dispatch")
class ParticipantListView(generic.ListView):
    model = User
    template_name = "events/participant_list.html"
    context_object_name = "participants"

    def get_queryset(self):
        return User.objects.filter(groups__name="Participant").order_by("username")


@method_decorator(role_required("Admin"), name="dispatch")
class ParticipantCreateView(generic.CreateView):
    model = User
    form_class = ParticipantCreateForm
    template_name = "events/participant_form.html"
    success_url = reverse_lazy("events:participant_list")

    def form_valid(self, form):
        user = form.save(commit=False)
        # By default, allow participant users to login; adjust is_active if needed
        user.is_active = True
        user.save()
        participant_group, _ = Group.objects.get_or_create(name="Participant")
        user.groups.add(participant_group)
        messages.success(self.request, "Participant user created.")
        return super().form_valid(form)


@method_decorator(role_required("Admin"), name="dispatch")
class ParticipantUpdateView(generic.UpdateView):
    model = User
    form_class = ParticipantUpdateForm
    template_name = "events/participant_form.html"
    success_url = reverse_lazy("events:participant_list")


@method_decorator(role_required("Admin"), name="dispatch")
class ParticipantDeleteView(generic.DeleteView):
    model = User
    template_name = "events/participant_delete.html"
    success_url = reverse_lazy("events:participant_list")

    def get_queryset(self):
        # limit deletion to users in Participant group to avoid accidental admin deletions
        return User.objects.filter(groups__name="Participant")


# -------------------------
# Categories: CRUD (organizer/admin)
# -------------------------
@method_decorator(role_required("Organizer", "Admin"), name="dispatch")
class CategoryListView(generic.ListView):
    model = Category
    template_name = "events/category_list.html"
    context_object_name = "categories"


@method_decorator(role_required("Organizer", "Admin"), name="dispatch")
class CategoryCreateView(generic.CreateView):
    model = Category
    fields = ["name", "description"]
    template_name = "events/category_form.html"
    success_url = reverse_lazy("events:category_list")


@method_decorator(role_required("Organizer", "Admin"), name="dispatch")
class CategoryUpdateView(generic.UpdateView):
    model = Category
    fields = ["name", "description"]
    template_name = "events/category_form.html"
    success_url = reverse_lazy("events:category_list")


@method_decorator(role_required("Organizer", "Admin"), name="dispatch")
class CategoryDeleteView(generic.DeleteView):
    model = Category
    template_name = "events/category_delete.html"
    success_url = reverse_lazy("events:category_list")


# -------------------------
# RSVP and user-specific views
# -------------------------
@login_required
def rsvp_view(request, pk):
    """
    Participant users can RSVP to an event. RSVP model uses unique_together to prevent duplicates.
    """
    event = get_object_or_404(Event, pk=pk)
    user = request.user
    # Only users in Participant group (or superuser) allowed
    if not (user.is_superuser or user.groups.filter(name="Participant").exists()):
        return HttpResponseForbidden("Only participants can RSVP to events.")

    if request.method == "POST":
        rsvp, created = RSVP.objects.get_or_create(user=user, event=event)
        if created:
            messages.success(request, "RSVP confirmed. A confirmation email will be sent.")
        else:
            messages.info(request, "You have already RSVP'd to this event.")
        return redirect("events:event_detail", pk=pk)

    return HttpResponseForbidden("Invalid method")


@login_required
def my_rsvps(request):
    """
    Show RSVPs for the logged-in user (participant dashboard).
    """
    rsvps = request.user.rsvps.select_related("event__category").all()
    return render(request, "events/rsvp_events.html", {"rsvps": rsvps})


# -------------------------
# Dashboards
# -------------------------
@role_required("Admin")
def admin_dashboard(request):
    today = timezone.localdate()
    total_users = User.objects.count()
    total_events = Event.objects.count()
    upcoming = Event.objects.filter(date__gte=today).count()
    past = Event.objects.filter(date__lt=today).count()
    events = Event.objects.select_related("category").prefetch_related("rsvps__user").all()[:50]
    return render(request, "events/dashboard_admin.html", {
        "total_users": total_users,
        "total_events": total_events,
        "upcoming": upcoming,
        "past": past,
        "events": events,
    })


@role_required("Organizer")
def organizer_dashboard(request):
    events = Event.objects.select_related("category").prefetch_related("rsvps__user").all()
    categories = Category.objects.all()
    return render(request, "events/dashboard_organizer.html", {
        "events": events,
        "categories": categories,
    })


@role_required("Participant")
def participant_dashboard(request):
    rsvps = request.user.rsvps.select_related("event__category").all()
    return render(request, "events/dashboard_participant.html", {"rsvps": rsvps})


# -------------------------
# JSON endpoint for interactive dashboard (optional)
# -------------------------
@login_required
def dashboard_data(request):
    """
    Returns JSON list of events according to type:
      ?type=all | upcoming | past | today
    """
    typ = request.GET.get("type", "all")
    today = timezone.localdate()
    qs = Event.objects.select_related("category").prefetch_related("rsvps__user")
    if typ == "upcoming":
        qs = qs.filter(date__gte=today)
    elif typ == "past":
        qs = qs.filter(date__lt=today)
    elif typ == "today":
        qs = qs.filter(date=today)

    data = []
    for ev in qs.order_by("date", "time")[:50]:
        data.append({
            "id": ev.id,
            "name": ev.name,
            "date": ev.date.isoformat(),
            "time": ev.time.isoformat() if ev.time else "",
            "location": ev.location,
            "category": ev.category.name if ev.category else None,
            "participants_count": ev.rsvps.count(),
        })
    return JsonResponse({"events": data})