from decimal import Decimal
import datetime

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin import widgets

from ias.models import Sighting, Taxon
from ias.exif_utils import get_lat_lon, get_datetime
from ias import widgets as ias_widgets

from EXIF import process_file


class SightingForm(forms.ModelForm):
    image = forms.FileField(help_text="Must be less than 1MB.")

    get_coords_from_photo = forms.BooleanField(
        required=False,
        initial=True,
        label="Get GPS from photo",
        help_text="Only available if your camera supports GPS.")
    lat = forms.DecimalField(
        max_digits=20,
        required=False,
        widget=forms.TextInput(attrs={
            'maxlength':20,
        }))
    lon = forms.DecimalField(
        max_digits=20,
        required=False,
        widget=forms.TextInput(attrs={
            'maxlength':20,
        }))
    map_picker = forms.CharField(
        widget=ias_widgets.GoogleLatLon(
            lat_name='lat', lon_name='lon'),
        required=False,
        help_text="Click on the map to choose a point",
        label="Click a point")

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
        exclude = ('photo', 'has_completed_questionnaire',
                   'datetime', 'verified')
        fields = (
            'taxon', 'email', 'contactable', 'image',
            'get_coords_from_photo', 'lat', 'lon', 'map_picker',
            'get_datetime_from_photo', 'date_time'
        )

    def clean(self):
        """{'image': <InMemoryUploadedFile: Photo 04-08-2011 19 51 15.jpeg
        (image/jpeg)>, 'lon': None, 'taxon': <Taxon: Family: Fallopia>,
        'datetime': u"[u'', u'']", 'lat': None, 'contactable': True,
        'get_coords_from_photo': True, 'get_datetime_from_photo': True,
        'email': u'steve@synfinity.net'}"""
        c_data = self.cleaned_data
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
            import logging
            logging.error(e)
            exif = None

        if c_data.get('get_coords_from_photo') and exif:
# User thinks there is GPS data in EXIF, and we have EXIF
            lat, lon = get_lat_lon(exif)
            if lat and lon:
                c_data['lat'] = Decimal(str(lat))
                c_data['lon'] = Decimal(str(lon))
            else:
# There isn't! Uncheck the box (set False) (doesn't work.. hm.)
                msg = "No GPS info in EXIF data. Please add manually! :-(" 
                self._errors["get_coords_from_photo"] = self.error_class(
                    [msg])
                c_data["get_coords_from_photo"] = False
        elif c_data.get('get_coords_from_photo') and not exif:
# User thinks there is EXIF but there isnt any
            msg = "No EXIF data available to get GPS info :-(" 
            self._errors["get_coords_from_photo"] = self.error_class(
                [msg])
            c_data["get_coords_from_photo"] = False
        elif not c_data['lon'] or not c_data['lat']:
# User put in one of lat/lon but not both
            msg = "Must set Lat/Long coordinates!" 
            self._errors["lat"] = self.error_class(
                [msg])
            del c_data["lat"]
            self._errors["lon"] = self.error_class(
                [msg])
            del c_data["lon"]
        else:
# Didn't expect EXIF, all ok.
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

        return c_data


class RegisterTaxonForm(forms.ModelForm):

    class Meta:
        model = Taxon
        exclude = ('active', 'style_name', 'style_json')


class AuthenticationRegisterForm(forms.Form):
    username = forms.CharField(label=("Email"), max_length=30)
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput)
