from django import forms

from ias.models import Sighting


class SightingForm(forms.ModelForm):
    class Meta:
        model = Sighting
