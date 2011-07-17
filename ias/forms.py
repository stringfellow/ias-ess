from django import forms

from ias.models import Sighting, Taxon


class SightingForm(forms.ModelForm):
    photo = forms.FileField()

    class Meta:
        model = Sighting
        exclude = ('photo', 'has_completed_questionnaire')


class RegisterTaxonForm(forms.ModelForm):

    class Meta:
        model = Taxon
        exclude = ('active', 'style_name', 'style_json')
