from django import forms
from django.contrib.auth.forms import AuthenticationForm

from ias.models import Sighting, Taxon


class SightingForm(forms.ModelForm):
    image = forms.FileField()
    get_coords_from_photo = forms.BooleanField(
        required=False,
        initial=True)
    lat = forms.DecimalField(
        max_digits=11,
        required=False)
    lon = forms.DecimalField(
        max_digits=11,
        required=False)

    class Meta:
        model = Sighting
        exclude = ('photo', 'has_completed_questionnaire')
        fields = ('taxon', 'email', 'contactable', 'image',
                  'get_coords_from_photo', 'lat', 'lon')


class RegisterTaxonForm(forms.ModelForm):

    class Meta:
        model = Taxon
        exclude = ('active', 'style_name', 'style_json')


class AuthenticationRegisterForm(AuthenticationForm):
    username = forms.CharField(label=("Email"), max_length=30)
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput)
    
    def clean(self):
        register = self.cleaned_data.get('register', None)
        login = self.cleaned_data.get('login', None)

        if login:
            return super(AuthenticationRegisterForm, self).clean()
        return self.cleaned_data

