from django.db import models


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

    def __str__(self):
        return self.full_name


class BookingRequest(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    pet_name = models.CharField(max_length=100)
    pet_breed = models.CharField(max_length=100)
    pet_weight_lbs = models.PositiveIntegerField()
    pet_age_years = models.PositiveIntegerField()

    services = models.ManyToManyField(Service)

    availability_notes = models.TextField()
    grooming_frequency = models.CharField(max_length=100)
    special_needs = models.TextField(blank=True)

    STATUS_CHOICES = [
        ("new", "New"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.full_name} - {self.pet_name}"