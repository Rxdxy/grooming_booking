from django.shortcuts import redirect, render

from .forms import BookingRequestForm
from .models import BookingRequest, Client


def book_request(request):
    if request.method == "POST":
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            client = Client.objects.create(
                full_name=form.cleaned_data["full_name"],
                address=form.cleaned_data["address"],
                phone=form.cleaned_data["phone"],
            )

            booking = BookingRequest.objects.create(
                client=client,
                pet_name=form.cleaned_data["pet_name"],
                pet_breed=form.cleaned_data["pet_breed"],
                pet_weight_lbs=form.cleaned_data["pet_weight_lbs"],
                pet_age_years=form.cleaned_data["pet_age_years"],
                availability_notes=form.cleaned_data["availability_notes"],
                grooming_frequency=form.cleaned_data["grooming_frequency"],
                special_needs=form.cleaned_data["special_needs"],
            )

            booking.services.set(form.cleaned_data["services"])
            return redirect("book_success")
    else:
        form = BookingRequestForm()

    return render(request, "booking_app/book_request.html", {"form": form})


def book_success(request):
    return render(request, "booking_app/book_success.html")