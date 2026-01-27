from django.db import models

# Create your models here.
class Client(models.Model):
    full_name = models.CharField(max_length=120)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)

    def __str__(self):
        return self.full_name

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name