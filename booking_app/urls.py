from django.urls import path
from . import views


urlpatterns = [
    path("book/", views.book_request, name="book_request"),
    path("book/success/", views.book_success, name="book_success"),
    path("calendar/", views.calendar_dashboard, name="calendar_dashboard"),
    path("api/calendar-events/", views.calendar_events, name="calendar_events"),
    path(
        "availability/",
        views.availability_dashboard,
        name="availability_dashboard",
    ),
    path(
        "api/availability-events/",
        views.availability_events,
        name="availability_events",
    ),
    path(
        "api/availability-slots/",
        views.availability_slots,
        name="availability_slots",
    ),
    path(
        "applications/",
        views.applications_list,
        name="applications_list",
    ),
    path(
        "clients/",
        views.clients_list,
        name="clients_list",
    ),
    path("apply/", views.apply, name="apply"),
    path("apply/success/", views.apply_success, name="apply_success"),
    path(
        "api/pending-applications/",
        views.pending_applications,
        name="pending_applications",
    ),
    path(
        "api/application/<int:app_id>/action/",
        views.application_action,
        name="application_action",
    ),
    path(
        "api/booking/<int:booking_id>/action/",
        views.booking_action,
        name="booking_action",
    ),
    path(
        "api/client/<int:client_id>/action/",
        views.client_action,
        name="client_action",
    ),
    path("bookings/", views.bookings_list, name="bookings_list"),
    path("bookings_list/", views.bookings_list, name="bookings_list_legacy"),
    path(
        "api/booking-suggestions/",
        views.booking_suggestions,
        name="booking_suggestions",
    ),
]