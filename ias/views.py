from __future__ import with_statement
import time

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
    photo_file.seek(0)
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

    # seems like sometimes the finalization is not fast enough or 
    # perhaps doesn't block until it is finished. This is a horrid
    # but effective way to make sure we get the blob key
    # I'm sure there is a better way, expect finalize emits something?
    timeout = 0
    while photo_obj.blob_key == None and timeout < 30:
        timeout += 1
        time.sleep(0.5)
        photo_obj.blob_key = files.blobstore.get_blob_key(photo_store)
    photo_obj.verified = False
    photo_obj.save()
    return photo_obj


def sighting_add(request):
    """A user sees a thing, record it."""
    if request.method == 'POST':
        form = SightingForm(request.POST, request.FILES)
        if form.is_valid():
            sighting = form.save(commit=False)
            photo_obj = _save_photo(request.FILES['image'])
            sighting.photo = photo_obj
            sighting.datetime = form.cleaned_data['date_time']
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
