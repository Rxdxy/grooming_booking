from django import forms
from .models import NewClientApplication, Service, BookingRequest, Client


class BookingRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Allow views to pass the current user: BookingRequestForm(..., user=request.user)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Always refresh services queryset at runtime (avoid import-time evaluation)
        if "services" in self.fields:
            self.fields["services"].queryset = Service.objects.all()

        # Make date time fields render nicely if they appear in a step
        if "scheduled_start" in self.fields:
            self.fields["scheduled_start"].widget = forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            )
        if "scheduled_end" in self.fields:
            self.fields["scheduled_end"].widget = forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            )

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

    # IMPORTANT: queryset is set in __init__ so it never goes stale
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
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
            "address",
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

        full_name = (self.cleaned_data.get("full_name") or "").strip()
        phone = (self.cleaned_data.get("phone") or "").strip()
        address = (self.cleaned_data.get("address") or "").strip()

        # Attach creator (only if model supports it)
        if self.user and hasattr(instance, "created_by"):
            instance.created_by = self.user

        # Reuse an existing active client when possible
        client = None
        if phone:
            existing = Client.objects.filter(phone=phone, is_active=True).first()
            if existing:
                # If address is provided and differs, treat as a new client record
                if address and (existing.address or "").strip() != address:
                    client = None
                else:
                    client = existing

        if client is None:
            client = Client.objects.create(
                full_name=full_name or "Client",
                address=address,
                phone=phone,
            )

        instance.client = client

        # Ensure address is always set (model also enforces this)
        if not instance.address:
            instance.address = client.address

        # Auto-confirm for known active clients (keeps behavior consistent)
        if client.is_active:
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