from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", RedirectView.as_view(url="/calendar/", permanent=False)),
    path("django-admin/", admin.site.urls),
    path("", include("booking_app.urls")),
]