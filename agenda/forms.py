from django import forms
from django.contrib.localflavor.us.forms import USStateSelect, USZipCodeField, USPhoneNumberField

from agenda.models import Location, Event


class USLocationForm(forms.ModelForm):
    class Meta:
        model = Location

    state_province = USStateSelect()
    postal_code = USZipCodeField()


class USEventForm(forms.ModelForm):
    class Meta:
        model = Event

    phone = USPhoneNumberField()
