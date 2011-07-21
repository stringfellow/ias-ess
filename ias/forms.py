from django import forms
from django.contrib.auth.forms import AuthenticationForm

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


class AuthenticationRegisterForm(AuthenticationForm):
    username = forms.CharField(label=("Email"), max_length=30)
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput)
    
    def clean(self):
        register = self.cleaned_data.get('register', None)
        login = self.cleaned_data.get('login', None)

        if login:
            return super(AuthenticationRegisterForm, self).clean()
        return self.cleaned_data

