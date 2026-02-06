from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class NewClientApplication(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_DECLINED = "declined"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DECLINED, "Declined"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    full_name = models.CharField(max_length=120)
    address = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=30)

    pet_name = models.CharField(max_length=80)
    pet_breed = models.CharField(max_length=120)
    pet_weight_lbs = models.PositiveIntegerField(null=True, blank=True)
    pet_age_years = models.PositiveIntegerField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.status})"


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name


class Client(models.Model):
    full_name = models.CharField(max_length=120)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name


class BookingRequest(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    pet_name = models.CharField(max_length=100)
    pet_breed = models.CharField(max_length=100)
    pet_weight_lbs = models.PositiveIntegerField()
    pet_age_years = models.PositiveIntegerField()
    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)

    services = models.ManyToManyField(Service)

    
    special_needs = models.TextField(blank=True)

    STATUS_CHOICES = [
        ("new", "New"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("declined", "Declined"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()

        if not self.scheduled_start or not self.scheduled_end:
            return

        if self.scheduled_end <= self.scheduled_start:
            raise ValidationError("End time must be after start time.")

        overlap = (
            Q(scheduled_start__lt=self.scheduled_end)
            & Q(scheduled_end__gt=self.scheduled_start)
        )

        # Block overlaps with active bookings.
        active = Q(status__in=["new", "confirmed"])

        qs = BookingRequest.objects.filter(overlap & active)

        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError(
                "That time overlaps with an existing booking."
            )

    def save(self, *args, **kwargs):
        if not self.address:
            if self.client_id and self.client and self.client.address:
                self.address = self.client.address
            else:
                raise ValueError("BookingRequest requires an address")

        # Enforce guardrails (also runs `clean()`).
        self.full_clean()

        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client.full_name} - {self.pet_name}"