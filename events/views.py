from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Count, Q
from django.http import JsonResponse
from .models import Event, Participant, Category
from .forms import EventForm, ParticipantForm, CategoryForm
import datetime

# --- Events CRUD and List with optimized queries ---
class EventListView(generic.ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 20

    def get_queryset(self):
        qs = Event.objects.select_related("category").prefetch_related("participants")
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

        # annotate participant counts
        qs = qs.annotate(participant_count=Count("participants"))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # total participant associations across events (counts M2M rows)
        total_participants_assoc = Event.objects.aggregate(total=Count("participants"))["total"] or 0
        ctx["total_participants_assoc"] = total_participants_assoc
        ctx["categories"] = Category.objects.all()
        # preserve search/filter params
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
        return Event.objects.select_related("category").prefetch_related("participants")


class EventCreateView(generic.CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")


class EventUpdateView(generic.UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:event_list")


class EventDeleteView(generic.DeleteView):
    model = Event
    template_name = "events/event_delete.html"
    success_url = reverse_lazy("events:event_list")


# --- Participant CRUD ---
class ParticipantListView(generic.ListView):
    model = Participant
    template_name = "events/participant_list.html"
    context_object_name = "participants"


class ParticipantCreateView(generic.CreateView):
    model = Participant
    form_class = ParticipantForm
    template_name = "events/participant_form.html"
    success_url = reverse_lazy("events:participant_list")


class ParticipantUpdateView(generic.UpdateView):
    model = Participant
    form_class = ParticipantForm
    template_name = "events/participant_form.html"
    success_url = reverse_lazy("events:participant_list")


class ParticipantDeleteView(generic.DeleteView):
    model = Participant
    template_name = "events/participant_delete.html"
    success_url = reverse_lazy("events:participant_list")


# --- Category CRUD ---
class CategoryListView(generic.ListView):
    model = Category
    template_name = "events/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(generic.CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "events/category_form.html"
    success_url = reverse_lazy("events:category_list")


class CategoryUpdateView(generic.UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "events/category_form.html"
    success_url = reverse_lazy("events:category_list")


class CategoryDeleteView(generic.DeleteView):
    model = Category
    template_name = "events/category_delete.html"
    success_url = reverse_lazy("events:category_list")


# --- Organizer Dashboard ---
def dashboard(request):
    today = datetime.date.today()
    total_unique_participants = Participant.objects.count()
    total_events = Event.objects.count()
    upcoming_events_count = Event.objects.filter(date__gte=today).count()
    past_events_count = Event.objects.filter(date__lt=today).count()
    todays_events = Event.objects.filter(date=today).select_related("category").prefetch_related("participants")
    context = {
        "total_unique_participants": total_unique_participants,
        "total_events": total_events,
        "upcoming_events_count": upcoming_events_count,
        "past_events_count": past_events_count,
        "todays_events": todays_events,
    }
    return render(request, "events/dashboard.html", context)


def dashboard_data(request):
    """
    Returns JSON data for dynamic dashboard interactions.
    type param: all | upcoming | past | today
    """
    typ = request.GET.get("type", "all")
    today = datetime.date.today()
    qs = Event.objects.select_related("category").prefetch_related("participants")
    if typ == "upcoming":
        qs = qs.filter(date__gte=today)
    elif typ == "past":
        qs = qs.filter(date__lt=today)
    elif typ == "today":
        qs = qs.filter(date=today)
    # else all

    data = []
    for ev in qs.order_by("date", "time")[:50]:
        data.append({
            "id": ev.id,
            "name": ev.name,
            "date": ev.date.isoformat(),
            "time": ev.time.isoformat(),
            "location": ev.location,
            "category": ev.category.name if ev.category else None,
            "participants_count": ev.participants.count(),
        })
    return JsonResponse({"events": data})