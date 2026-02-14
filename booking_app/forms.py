from django import forms
from .models import NewClientApplication, Service, BookingRequest


class BookingRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
    full_name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your full name",
            }
        ),
    )
    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Street address",
            }
        ),
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "(702) 555-0123",
            }
        ),
    )

    pet_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Pet name",
            }
        ),
    )
    pet_breed = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Breed",
            }
        ),
    )
    pet_weight_lbs = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Weight in lbs",
            }
        ),
    )
    pet_age_years = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Age in years",
            }
        ),
    )

    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    
    special_needs = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Anything we should know?",
            }
        ),
    )

    class Meta:
        model = BookingRequest
        fields = (
            "full_name",
            "address",
            "phone",
            "pet_name",
            "pet_breed",
            "pet_weight_lbs",
            "pet_age_years",
            "services",
            "special_needs",
            "scheduled_start",
            "scheduled_end",
        )


    def save(self, commit=True):
        instance = super().save(commit=False)

        # Attach creator (Nazar when booking from calendar)
        if self.user and hasattr(instance, "created_by"):
            instance.created_by = self.user

        # Auto-confirm for existing active clients
        if instance.client_id and instance.client and instance.client.is_active:
            instance.status = "confirmed"

        if commit:
            instance.save()
            self.save_m2m()

        return instance


# New client application form
class NewClientApplicationForm(forms.ModelForm):
    class Meta:
        model = NewClientApplication
        fields = (
            "full_name",
            "address",
            "zip_code",
            "phone",
            "pet_name",
            "pet_breed",
            "pet_weight_lbs",
            "pet_age_years",
            "notes",
        )
        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Jane Doe",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "123 Main St, Chicago, IL",
                }
            ),
            "zip_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "60610",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "(555) 555-5555",
                }
            ),
            "pet_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Buddy",
                }
            ),
            "pet_breed": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Poodle",
                }
            ),
            "pet_weight_lbs": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "25",
                }
            ),
            "pet_age_years": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "4",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Anything Nazar should know?",
                }
            ),
        }