import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Case, IntegerField, Q, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import BookingRequestForm, NewClientApplicationForm
from .models import BookingRequest, Client, NewClientApplication, Service


def book_request(request):
    if request.method == "POST":
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    client = Client.objects.create(
                        full_name=form.cleaned_data["full_name"],
                        address=form.cleaned_data["address"],
                        phone=form.cleaned_data["phone"],
                    )

                    booking = form.save(commit=False)
                    booking.client = client

                    # Ensure address is stored on the booking (snapshot), so lists/copy work
                    if not getattr(booking, "address", ""):
                        booking.address = client.address

                    start_raw = request.POST.get("scheduled_start")
                    end_raw = request.POST.get("scheduled_end")

                    # Admin manual booking flow: accept datetime-local inputs
                    manual_start = request.POST.get("manual_start")
                    manual_end = request.POST.get("manual_end")

                    if not start_raw and manual_start:
                        start_raw = manual_start

                    if not end_raw and manual_end:
                        end_raw = manual_end

                    start_dt = None
                    if start_raw:
                        start_clean = start_raw.replace("Z", "")
                        start_dt = datetime.datetime.fromisoformat(start_clean)

                        tz = timezone.get_current_timezone()
                        if timezone.is_naive(start_dt):
                            start_dt = timezone.make_aware(start_dt, tz)
                        else:
                            start_dt = timezone.localtime(start_dt, tz)

                    end_dt = None
                    if end_raw:
                        end_clean = end_raw.replace("Z", "")
                        end_dt = datetime.datetime.fromisoformat(end_clean)

                        tz = timezone.get_current_timezone()
                        if timezone.is_naive(end_dt):
                            end_dt = timezone.make_aware(end_dt, tz)
                        else:
                            end_dt = timezone.localtime(end_dt, tz)

                    booking.scheduled_start = start_dt

                    if end_dt is None and start_dt is not None:
                        end_dt = start_dt + datetime.timedelta(hours=1)

                    booking.scheduled_end = end_dt

                    # Will raise ValidationError if it overlaps (guardrails)
                    booking.save()
                    form.save_m2m()

                return redirect("book_success")

            except ValidationError as e:
                msg = "; ".join(e.messages) if getattr(e, "messages", None) else str(e)
                form.add_error(None, msg)
    else:
        form = BookingRequestForm()

    return render(
        request,
        "booking_app/book_request.html",
        {
            "form": form,
            "services": Service.objects.all(),
        },
    )


def book_success(request):
    return render(request, "booking_app/book_success.html")


def apply(request):
    if request.method == "POST":
        form = NewClientApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("apply_success")
    else:
        form = NewClientApplicationForm()

    return render(
        request,
        "booking_app/apply.html",
        {"form": form},
    )


def apply_success(request):
    return render(request, "booking_app/apply_success.html")


def calendar_dashboard(request):
    return render(request, "booking_app/calendar.html")


def availability_dashboard(request):
    return render(request, "booking_app/availability.html")


@staff_member_required
def bookings_list(request):
    q = (request.GET.get("q") or "").strip()

    qs = BookingRequest.objects.select_related("client").prefetch_related("services")

    if q:
        qs = qs.filter(
            Q(client__full_name__icontains=q)
            | Q(pet_name__icontains=q)
            | Q(pet_breed__icontains=q)
            | Q(address__icontains=q)
        )

    qs = qs.annotate(
        _no_time=Case(
            When(scheduled_start__isnull=True, then=1),
            default=0,
            output_field=IntegerField(),
        )
    ).order_by("_no_time", "scheduled_start", "-created_at")

    return render(
        request,
        "booking_app/booking_list.html",
        {
            "bookings": qs,
            "q": q,
        },
    )


@staff_member_required
def applications_list(request):
    return render(
        request,
        "booking_app/applications_list.html",
    )


@staff_member_required
def booking_suggestions(request):
    q = (request.GET.get("q") or "").strip()

    if len(q) < 2:
        return JsonResponse({"items": []})

    qs = BookingRequest.objects.select_related("client").filter(
        Q(client__full_name__icontains=q)
        | Q(pet_name__icontains=q)
        | Q(pet_breed__icontains=q)
        | Q(address__icontains=q)
        | Q(client__address__icontains=q)
    )

    items = []
    seen = set()
    ql = q.lower()

    for b in qs.order_by("-created_at")[:80]:
        vals = [
            (b.client.full_name or "").strip(),
            (b.pet_name or "").strip(),
            (getattr(b, "pet_breed", "") or "").strip(),
            (getattr(b, "address", "") or "").strip(),
            (getattr(b.client, "address", "") or "").strip(),
        ]

        for s in vals:
            if not s:
                continue

            key = s.lower()
            if ql not in key:
                continue

            if key in seen:
                continue

            seen.add(key)
            items.append(s)

            if len(items) >= 8:
                break

        if len(items) >= 8:
            break

    return JsonResponse({"items": items})


def calendar_events(request):
    events = []

    bookings = (
        BookingRequest.objects.select_related("client")
        .exclude(status="declined")
        .exclude(scheduled_start__isnull=True)
    )

    for booking in bookings:
        start = timezone.localtime(booking.scheduled_start)
        end = timezone.localtime(booking.scheduled_end) if booking.scheduled_end else None

        title = f"{booking.pet_name} ({booking.client.full_name})"
        addr = booking.address or booking.client.address

        event = {
            "id": booking.id,
            "title": title,
            "start": start.isoformat(),
            "url": f"/django-admin/booking_app/bookingrequest/{booking.id}/change/",
            "extendedProps": {
                "booking_id": booking.id,
                "status": booking.status,
                "address": addr,
            },
        }

        # Backward compatible keys (safe if templates still reference them)
        event["address"] = addr
        event["status"] = booking.status

        if end is not None:
            event["end"] = end.isoformat()

        events.append(event)

    return JsonResponse(events, safe=False)


def availability_events(request):
    events = []

    bookings = (
        BookingRequest.objects.exclude(status="declined")
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

    return JsonResponse(events, safe=False)


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
        BookingRequest.objects.exclude(status="declined")
        .exclude(scheduled_start__isnull=True)
        .exclude(scheduled_end__isnull=True)
        .filter(scheduled_start__lt=range_end)
        .filter(scheduled_end__gt=range_start)
        .values_list("scheduled_start", "scheduled_end")
    )

    busy_blocks = []
    for s, e in busy_qs:
        busy_blocks.append((timezone.localtime(s, tz), timezone.localtime(e, tz)))

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


def _ensure_client_from_application(app):
    phone = (getattr(app, "phone", "") or "").strip()
    address = (getattr(app, "address", "") or "").strip()
    full_name = (getattr(app, "full_name", "") or "").strip()

    qs = Client.objects.all()

    if phone:
        qs = qs.filter(phone=phone)

    if address:
        qs = qs.filter(address=address)

    existing = qs.first()
    if existing:
        return existing

    return Client.objects.create(
        full_name=full_name,
        address=address,
        phone=phone,
    )


def pending_applications(request):
    apps = NewClientApplication.objects.filter(status="pending").order_by("-created_at")

    data = []
    for app in apps:
        created = getattr(app, "created_at", None)
        created_iso = created.isoformat() if created else None

        data.append(
            {
                "id": app.id,
                "name": (getattr(app, "full_name", "") or "").strip(),
                "zip_code": (getattr(app, "zip_code", "") or "").strip(),
                "address": (getattr(app, "address", "") or "").strip(),
                "created": created_iso,
                "admin_url": (
                    f"/django-admin/booking_app/newclientapplication/{app.id}/change/"
                ),
            }
        )

    return JsonResponse(data, safe=False)


@staff_member_required
@require_POST
def application_action(request, app_id):
    app = get_object_or_404(NewClientApplication, id=app_id)

    action = (request.POST.get("action") or "").strip().lower()
    if action not in {"approve", "decline"}:
        return JsonResponse({"ok": False, "error": "bad_action"}, status=400)

    if action == "approve":
        _ensure_client_from_application(app)
        app.status = "approved"
    else:
        app.status = "declined"

    app.save(update_fields=["status"])

    return JsonResponse({"ok": True, "status": app.status})


@staff_member_required
@require_POST
def booking_action(request, booking_id):
    booking = get_object_or_404(BookingRequest, id=booking_id)

    action = (request.POST.get("action") or "").strip().lower()
    if action not in {"confirm", "decline"}:
        return JsonResponse({"ok": False, "error": "bad_action"}, status=400)

    if action == "confirm":
        booking.status = "confirmed"
    else:
        booking.status = "declined"

    booking.save(update_fields=["status"])

    return JsonResponse({"ok": True, "status": booking.status})