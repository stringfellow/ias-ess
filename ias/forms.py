from django import forms

from ias.models import Taxon


class SightingForm(forms.Form):
    taxon = forms.ModelChoiceField(Taxon.objects.all())
