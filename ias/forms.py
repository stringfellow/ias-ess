from django import forms

from ias.models import Sighting, Taxon


class SightingForm(forms.ModelForm):
    photo = forms.FileField()

    class Meta:
        model = Sighting
        exclude = ('photo',)


class RegisterTaxonForm(forms.ModelForm):

    class Meta:
        model = Taxon
        exclude = ('active',)
