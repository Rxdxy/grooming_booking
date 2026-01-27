from django.urls import path
from . import views

urlpatterns = [
    path("book/", views.book_request, name="book_request"),
    path("book/success/", views.book_success, name="book_success"),
    path("calendar/", views.calendar_dashboard, name="calendar_dashboard"),
]