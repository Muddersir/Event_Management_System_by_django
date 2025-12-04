from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from .models import Event, Category, RSVP
from .forms import EventForm

# Role check mixin
class GroupRequiredMixin(UserPassesTestMixin):
    group_names = []

    def test_func(self):
        user = self.request.user
        if user.is_superuser:
            return True
        return any(user.groups.filter(name=g).exists() for g in self.group_names)

    def handle_no_permission(self):
        return redirect("accounts:login")

# --- Events CBVs ---
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

        return qs.annotate(participant_count=Count("attendees", distinct=True))

    def get_context_data(self, **kwargs):
        """
        Provide a boolean `can_add_event` to the template so we don't call
        QuerySet methods or use parentheses inside template tags.
        """
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        can_add = False
        if user.is_authenticated:
            # Safe to call QuerySet methods here
            can_add = user.is_superuser or user.groups.filter(name="Organizer").exists()
        ctx["can_add_event"] = can_add
        return ctx

class EventDetailView(generic.DetailView):
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"

    def get_queryset(self):
        return Event.objects.select_related("category").prefetch_related("rsvps__user")

class EventCreateView(LoginRequiredMixin, GroupRequiredMixin, generic.CreateView):
    group_names = ["Organizer", "Admin"]
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")

class EventUpdateView(LoginRequiredMixin, GroupRequiredMixin, generic.UpdateView):
    group_names = ["Organizer", "Admin"]
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")

class EventDeleteView(LoginRequiredMixin, GroupRequiredMixin, generic.DeleteView):
    group_names = ["Organizer", "Admin"]
    model = Event
    template_name = "events/event_delete.html"
    success_url = reverse_lazy("events:event_list")

# Category CBVs
class CategoryListView(LoginRequiredMixin, GroupRequiredMixin, generic.ListView):
    group_names = ["Organizer", "Admin"]
    model = Category
    template_name = "events/category_list.html"
    context_object_name = "categories"

class CategoryCreateView(LoginRequiredMixin, GroupRequiredMixin, generic.CreateView):
    group_names = ["Organizer", "Admin"]
    model = Category
    fields = ["name", "description"]
    template_name = "events/category_form.html"
    success_url = reverse_lazy("events:category_list")

class CategoryUpdateView(LoginRequiredMixin, GroupRequiredMixin, generic.UpdateView):
    group_names = ["Organizer", "Admin"]
    model = Category
    fields = ["name", "description"]
    template_name = "events/category_form.html"
    success_url = reverse_lazy("events:category_list")

class CategoryDeleteView(LoginRequiredMixin, GroupRequiredMixin, generic.DeleteView):
    group_names = ["Organizer", "Admin"]
    model = Category
    template_name = "events/category_delete.html"
    success_url = reverse_lazy("events:category_list")

# RSVP as a minimal CBV (post only)
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name="dispatch")
class RSVPView(View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user
        if not (user.is_superuser or user.groups.filter(name="Participant").exists()):
            messages.error(request, "Only participants can RSVP.")
            return redirect("events:event_detail", pk=pk)
        rsvp, created = RSVP.objects.get_or_create(user=user, event=event)
        if created:
            messages.success(request, "RSVP successful.")
        else:
            messages.info(request, "You already RSVP'd.")
        return redirect("events:event_detail", pk=pk)

# My RSVPs (participant dashboard)
class MyRSVPsView(LoginRequiredMixin, generic.ListView):
    template_name = "events/rsvp_events.html"
    context_object_name = "rsvps"

    def get_queryset(self):
        return self.request.user.rsvps.select_related("event__category").all()

# dashboards can remain CBVs as well
class AdminDashboardView(LoginRequiredMixin, GroupRequiredMixin, generic.TemplateView):
    group_names = ["Admin"]
    template_name = "events/dashboard_admin.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        ctx["total_users"] = __import__("django.contrib.auth").contrib.auth.get_user_model().objects.count()
        ctx["total_events"] = Event.objects.count()
        ctx["upcoming"] = Event.objects.filter(date__gte=today).count()
        ctx["past"] = Event.objects.filter(date__lt=today).count()
        ctx["events"] = Event.objects.select_related("category").prefetch_related("rsvps__user").all()[:50]
        return ctx

class OrganizerDashboardView(LoginRequiredMixin, GroupRequiredMixin, generic.TemplateView):
    group_names = ["Organizer"]
    template_name = "events/dashboard_organizer.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["events"] = Event.objects.select_related("category").prefetch_related("rsvps__user").all()
        ctx["categories"] = Category.objects.all()
        return ctx

class ParticipantDashboardView(LoginRequiredMixin, GroupRequiredMixin, generic.TemplateView):
    group_names = ["Participant"]
    template_name = "events/dashboard_participant.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["rsvps"] = self.request.user.rsvps.select_related("event__category").all()
        return ctx