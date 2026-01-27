import datetime


from django.shortcuts import redirect, render
from django.http import JsonResponse
from .forms import BookingRequestForm
from .models import BookingRequest, Client
from django.utils import timezone


def book_request(request):
    if request.method == "POST":
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            client = Client.objects.create(
                full_name=form.cleaned_data["full_name"],
                address=form.cleaned_data["address"],
                phone=form.cleaned_data["phone"],
            )

            booking = BookingRequest.objects.create(
                client=client,
                pet_name=form.cleaned_data["pet_name"],
                pet_breed=form.cleaned_data["pet_breed"],
                pet_weight_lbs=form.cleaned_data["pet_weight_lbs"],
                pet_age_years=form.cleaned_data["pet_age_years"],
                availability_notes=form.cleaned_data["availability_notes"],
                grooming_frequency=form.cleaned_data["grooming_frequency"],
                special_needs=form.cleaned_data["special_needs"],
            )

            booking.services.set(form.cleaned_data["services"])
            return redirect("book_success")
    else:
        form = BookingRequestForm()

    return render(request, "booking_app/book_request.html", {"form": form})


def book_success(request):
    return render(request, "booking_app/book_success.html")

def calendar_dashboard(request):
    return render(request, "booking_app/calendar.html")

def availability_dashboard(request):
    return render(request, "booking_app/availability.html")

def calendar_events(request):
    events = []
    bookings = BookingRequest.objects.select_related("client").all()

    for booking in bookings:
        start = booking.scheduled_start
        end = booking.scheduled_end

        if start is None:
            continue

        title = f"{booking.pet_name} ({booking.client.full_name})"

        event = {
            "id": booking.id,
            "title": title,
            "start": start.isoformat(),
            "url": f"/admin/booking_app/bookingrequest/{booking.id}/change/",
        }

        if end is not None:
            event["end"] = end.isoformat()

        events.append(event)

def availability_events(request):
    events = []

    bookings = (
        BookingRequest.objects
        .filter(status__in=["pending", "confirmed"])
        .exclude(scheduled_start__isnull=True)
        .exclude(scheduled_end__isnull=True)
    )

    for booking in bookings:
        events.append(
            {
                "title": "Booked",
                "start": booking.scheduled_start.isoformat(),
                "end": booking.scheduled_end.isoformat(),
            }
        )

def availability_slots(request):
    tz = timezone.get_current_timezone()

    start_str = request.GET.get("start")
    end_str = request.GET.get("end")

    if not start_str or not end_str:
        return JsonResponse([], safe=False)

    try:
        range_start = datetime.datetime.fromisoformat(start_str)
        range_end = datetime.datetime.fromisoformat(end_str)
    except ValueError:
        return JsonResponse([], safe=False)

    if timezone.is_naive(range_start):
        range_start = timezone.make_aware(range_start, tz)
    else:
        range_start = timezone.localtime(range_start, tz)

    if timezone.is_naive(range_end):
        range_end = timezone.make_aware(range_end, tz)
    else:
        range_end = timezone.localtime(range_end, tz)

    busy_qs = (
        BookingRequest.objects
        .exclude(scheduled_start__isnull=True)
        .exclude(scheduled_end__isnull=True)
        .filter(scheduled_start__lt=range_end)
        .filter(scheduled_end__gt=range_start)
        .values_list("scheduled_start", "scheduled_end")
    )

    busy_blocks = []
    for s, e in busy_qs:
        busy_blocks.append(
            (timezone.localtime(s, tz), timezone.localtime(e, tz))
        )

    def overlaps(a_start, a_end):
        for b_start, b_end in busy_blocks:
            if a_start < b_end and a_end > b_start:
                return True
        return False

    slot_minutes = 60
    open_hour = 9
    close_hour = 18

    events = []
    day = range_start.date()
    last_day = range_end.date()

    while day <= last_day:
        day_start = timezone.make_aware(
            datetime.datetime.combine(day, datetime.time(0, 0)),
            tz,
        )

        work_start = day_start.replace(hour=open_hour, minute=0)
        work_end = day_start.replace(hour=close_hour, minute=0)

        cur = work_start
        step = datetime.timedelta(minutes=slot_minutes)

        while cur + step <= work_end:
            slot_start = cur
            slot_end = cur + step

            in_range = slot_start >= range_start and slot_end <= range_end
            if in_range and not overlaps(slot_start, slot_end):
                events.append(
                    {
                        "title": "Available",
                        "start": slot_start.isoformat(),
                        "end": slot_end.isoformat(),
                    }
                )

            cur = slot_end

        day = day + datetime.timedelta(days=1)

    return JsonResponse(events, safe=False)