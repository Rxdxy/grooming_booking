from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from booking_app.views import availability_dashboard, calendar_dashboard

urlpatterns = [
    path("django-admin/", admin.site.urls),

    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("", availability_dashboard, name="home"),
    path("calendar/", login_required(calendar_dashboard), name="calendar_dashboard"),

    path("", include("booking_app.urls")),
]