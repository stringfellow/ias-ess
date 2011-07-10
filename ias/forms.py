from django import forms

from ias.models import Sighting


class SightingForm(forms.ModelForm):
    photo = forms.FileField()

    class Meta:
        model = Sighting
        exclude = ('photo',)
