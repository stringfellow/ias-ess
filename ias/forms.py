from decimal import Decimal
import datetime

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin import widgets

from ias.models import Sighting, Taxon
from ias.exif_utils import get_lat_lon, get_datetime

from EXIF import process_file

class SightingForm(forms.ModelForm):
    image = forms.FileField()
    get_coords_from_photo = forms.BooleanField(
        required=False,
        initial=True,
        label="Get GPS from photo",
        help_text="Only available if your camera supports GPS.")
    lat = forms.DecimalField(
        max_digits=11,
        required=False)
    lon = forms.DecimalField(
        max_digits=11,
        required=False)
    get_datetime_from_photo = forms.BooleanField(
        required=False,
        initial=True,
        label="Get Date/time from photo",
        help_text="Likely to be available; will use current date/time.")
    date_time = forms.DateTimeField(
        widget=widgets.AdminSplitDateTime,
        required=False)

    class Meta:
        model = Sighting
        exclude = ('photo', 'has_completed_questionnaire', 'datetime')
        fields = (
            'taxon', 'email', 'contactable', 'image',
            'get_coords_from_photo', 'lat', 'lon',
            'get_datetime_from_photo', 'date_time'
        )

    def clean(self):
        """{'image': <InMemoryUploadedFile: Photo 04-08-2011 19 51 15.jpeg
        (image/jpeg)>, 'lon': None, 'taxon': <Taxon: Family: Fallopia>,
        'datetime': u"[u'', u'']", 'lat': None, 'contactable': True,
        'get_coords_from_photo': True, 'get_datetime_from_photo': True,
        'email': u'steve@synfinity.net'}"""
        c_data = self.cleaned_data
        import logging
        logging.debug(c_data)
        logging.debug(self._errors)
        if c_data.get('contactable', False) and \
            not c_data.get('email', ''):
            msg = "Please add email address if you want to be contacted!"
            self._errors["email"] = self.error_class([msg])
            del c_data['email']

        exif = None
        try:
            f = c_data['image'].file
            f.seek(0)
            exif = process_file(f)
        except Exception, e:
            exif = None

        if c_data.get('get_coords_from_photo') and exif:
            lat, lon = get_lat_lon(exif)
            if lat and lon:
                c_data['lat'] = Decimal(str(lat))
                c_data['lon'] = Decimal(str(lon))
            else:
                msg = "No GPS info in EXIF data. Please add manually! :-(" 
                self._errors["get_coords_from_photo"] = self.error_class(
                    [msg])
                del c_data["get_coords_from_photo"]
        elif c_data.get('get_coords_from_photo') and not exif:
            msg = "No EXIF data available to get GPS info :-(" 
            self._errors["get_coords_from_photo"] = self.error_class(
                [msg])
            del c_data["get_coords_from_photo"]
        elif not c_data['lon'] or not c_data['lat']:
            msg = "Must set Lat/Long coordinates!" 
            self._errors["lat"] = self.error_class(
                [msg])
            del c_data["lat"]
            self._errors["lon"] = self.error_class(
                [msg])
            del c_data["lon"]
        else:
            c_data['lat'] = Decimal(c_data['lat'])
            c_data['lon'] = Decimal(c_data['lon'])


        if c_data.get('get_datetime_from_photo') and exif:
            dt = get_datetime(exif)
            if dt:
                c_data['date_time'] = str(dt)
            else:
                msg = "No date-time available in EXIF data. Please add manually! :-("
                self._errors["get_datetime_from_photo"] = self.error_class(
                    [msg])
                del c_data["get_datetime_from_photo"]
        elif c_data.get('get_datetime_from_photo') and not exif:
            msg = "No EXIF data available to get date-time info :-(" 
            self._errors["get_datetime_from_photo"] = self.error_class(
                [msg])
            del c_data["get_datetime_from_photo"]

        import logging
        logging.debug(c_data)
        return c_data


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

