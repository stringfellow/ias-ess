from __future__ import with_statement

from decimal import Decimal
from StringIO import StringIO

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import login as login_view
from django.http import HttpResponseRedirect
from django.template import RequestContext

from google.appengine.api import images as images_api
from google.appengine.api import files
from google.appengine.ext import blobstore

from ias.models import Photo, Sighting, Taxon, TaxonExpert
from ias.forms import SightingForm, RegisterTaxonForm, AuthenticationRegisterForm
from ias.utils import tweak_google_form

from EXIF import process_file

def home(request):
    latest_sightings = []
    latest_taxa = []
    if request.method == 'POST':
        form = AuthenticationRegisterForm(request.POST)
        if form.is_valid():
            register = form.data.get('register', None)
            login = form.data.get('login', None)
            if register:
                return HttpResponseRedirect(reverse('registration_register'))
            if login:
                return login_view(request)
    else:
        form = AuthenticationRegisterForm()
        
    return render_to_response(
        'home.html',
        {
            'form': form,
            'action': reverse('home')
        },
        context_instance=RequestContext(request)
    )


def _save_photo(image):
    photo_file = image
    photo_size = photo_file.size
    photo_type = photo_file.content_type
    photo_store = files.blobstore.create(
        mime_type=photo_type,
        _blobinfo_uploaded_filename=photo_file.name)

    with files.open(photo_store, 'a') as f:
        data = photo_file.read(blobstore.MAX_BLOB_FETCH_SIZE)
        while data:
            f.write(data)
            data = photo_file.read(blobstore.MAX_BLOB_FETCH_SIZE)

    files.finalize(photo_store)
    photo_obj = Photo()
    photo_obj.photo = None
    photo_obj.blob_key = files.blobstore.get_blob_key(photo_store)
    photo_obj.verified = False
    photo_obj.save()
    return photo_obj

	
def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    values = value.values

    d0 = values[0].num
    d1 = values[0].den
    d = float(d0) / float(d1)
    
    m0 = values[1].num
    m1 = values[1].den
    m = float(m0) / float(m1)

    s0 = values[2].num
    s1 = values[2].den
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def get_lat_lon(exif):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None

    if len(filter(lambda k: str(k).startswith('GPS'), exif.keys())):
        gps_latitude = exif["GPS GPSLatitude"]
        gps_latitude_ref = exif["GPS GPSLatitudeRef"]
        gps_longitude = exif["GPS GPSLongitude"]
        gps_longitude_ref = exif["GPS GPSLongitudeRef"]

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref.values != "N":
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref.values != "E":
                lon = 0 - lon

    return lat, lon

def sighting_add(request):
    """A user sees a thing, record it."""
    if request.method == 'POST':
        form = SightingForm(request.POST, request.FILES)
        if form.is_valid():
            sighting = form.save(commit=False)
            photo_obj = _save_photo(request.FILES['image'])
            sighting.photo = photo_obj
            if form.cleaned_data['get_coords_from_photo']:
                f = request.FILES['image'].file
                f.seek(0)
                exif = process_file(f)
                lat, lon = get_lat_lon(exif)
                sighting.lat = Decimal(str(lat))
                sighting.lon = Decimal(str(lon))
            sighting.save()
            return HttpResponseRedirect(reverse(
                'ias-sighting-detail',
                args=[sighting.pk])
            )
    else:
        form = SightingForm()
    return render_to_response(
        'ias/sighting.html',
        {
            'form': form,
            # action="." does not work with jQuery mobile as it does not
            # call the URL with a slash on the end which then causes a
            # Django error
            'action': reverse('ias-sighting-add')
        },
        context_instance=RequestContext(request)
        )

def sighting_detail(request, pk):
    sighting = get_object_or_404(Sighting, pk=pk)
    if not sighting.has_completed_questionnaire:
        google_form = tweak_google_form(sighting.taxon.questionnaire, pk)
        # set this to true now because this should be completed by sighter
        # and no one else. tough shit if they miss it first time...
        sighting.has_completed_questionnaire = True
        sighting.save()
    else:
        google_form = None

    others = Sighting.objects.filter(taxon=sighting.taxon).exclude(
        pk=sighting.pk)

    return render_to_response(
        'ias/sighting_detail.html',
        {
            'google_form': google_form,
            'sighting': sighting,
            'others': others,
        },
        context_instance=RequestContext(request)
        )

@login_required
def taxon_add(request):
    """The start of flow for registering a new taxon."""
    if request.method == 'POST':
        form = RegisterTaxonForm(request.POST)
        if form.is_valid():
            taxon = form.save()
            TaxonExpert.objects.create(expert=request.user, taxon=taxon)
            return HttpResponseRedirect(reverse(
                'ias-taxon-detail',
                args=[taxon.pk])
            )
    else:
        form = RegisterTaxonForm()

    return render_to_response(
        'ias/taxon_register.html',
        {
            'form': form,
            'all_taxa': Taxon.objects.all(),
            'my_taxa': TaxonExpert.objects.filter(expert=request.user),
        },
        context_instance=RequestContext(request))

def taxon_detail(request, pk):
    """Show taxa..."""

    taxon = get_object_or_404(Taxon, pk=pk)
    taxon_experts = TaxonExpert.objects.filter(taxon=taxon)
    experts = User.objects.filter(pk__in=taxon_experts)

    return render_to_response(
        'ias/taxon_registered.html',
        {
            'taxon': taxon,
            'experts': experts,
        },
        context_instance=RequestContext(request)
        )


def map(request):
    taxa = Taxon.objects.all()
    return render_to_response(
        'ias/map.html',
        {
            'taxa': taxa,
        },
        context_instance=RequestContext(request)
    )
