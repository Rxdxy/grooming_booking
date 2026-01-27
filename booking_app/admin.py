from django.contrib import admin

from .models import BookingRequest, Client, Service


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone")
    search_fields = ("full_name", "phone")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("client", "pet_name", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("client__full_name", "pet_name", "client__phone")
    filter_horizontal = ("services",)