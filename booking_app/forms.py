from django import forms
from .models import Service


class BookingRequestForm(forms.Form):
    # Client
    full_name = forms.CharField(max_length=120)
    address = forms.CharField(max_length=255)
    phone = forms.CharField(max_length=30)

    # Pet
    pet_name = forms.CharField(max_length=100)
    pet_breed = forms.CharField(max_length=100)
    pet_weight_lbs = forms.IntegerField(min_value=1)
    pet_age_years = forms.IntegerField(min_value=0)

    # Booking details
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    availability_notes = forms.CharField(widget=forms.Textarea)
    grooming_frequency = forms.CharField(max_length=100)
    special_needs = forms.CharField(required=False, widget=forms.Textarea)