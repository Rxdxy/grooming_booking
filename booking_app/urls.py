from django.urls import path
from . import views

urlpatterns = [
    path("book/", views.book_request, name="book_request"),
    path("book/success/", views.book_success, name="book_success"),
    path("calendar/", views.calendar_dashboard, name="calendar_dashboard"),
    path("api/calendar-events/", views.calendar_events, name="calendar_events"),
    path("availability/", views.availability_dashboard, 
        name="availability_dashboard"),
    path("api/availability-events/", views.availability_events,
        name="availability_events"),
    path("api/availability-slots/", views.availability_slots,
        name="availability_slots"),
    path("apply/", views.apply, name="apply"),
    path("apply/success/", views.apply_success, name="apply_success"),
    
]