from django.contrib import admin

from .models import BookingRequest, Client, NewClientApplication, Service

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "is_active")
    list_filter = ("is_active",)
    search_fields = ("full_name", "phone")
    actions = ("mark_active", "mark_inactive")

    @admin.action(description="Mark selected clients as Active")
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Mark selected clients as Inactive")
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)


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


@admin.register(NewClientApplication)
class NewClientApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("full_name", "phone", "address", "pet_name")

    fieldsets = (
        (
            "Applicant",
            {
                "fields": (
                    "full_name",
                    "address",
                    "phone",
                )
            },
        ),
        (
            "Pet",
            {
                "fields": (
                    "pet_name",
                    "pet_breed",
                    "pet_weight_lbs",
                    "pet_age_years",
                )
            },
        ),
        (
            "Notes",
            {
                "fields": (
                    "notes",
                )
            },
        ),
        (
            "Decision",
            {
                "fields": (
                    "status",
                )
            },
        ),
    )