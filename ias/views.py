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

from ias.models import Photo, Sighting, Taxon, TaxonExpert
from ias.forms import SightingForm, RegisterTaxonForm, AuthenticationRegisterForm
from ias.utils import tweak_google_form, save_photo
from search.core import search

def home(request):
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


def resave(request):
    for obj in Taxon.objects.all():
        obj.save()
    for obj in Sighting.objects.all():
        obj.save()


def sighting_add(request):
    if request.method == 'POST':
        form = SightingForm(request.POST, request.FILES)
        if form.is_valid():
            sighting = form.save(commit=False)
            photo_obj = save_photo(request.FILES['image'])
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


def sighting_detail(request, pk, in_app=False):
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
            'in_app': in_app,
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
    taxa = Taxon.actives.all()
    return render_to_response(
        'ias/map.html',
        {
            'taxa': taxa,
        },
        context_instance=RequestContext(request)
    )


def search_db(request):
    search_str = request.GET.get('q', '')
    search_str.replace('+', ' ')
    
    taxa_sw = set(search(Taxon, search_str, search_index='startswith_index'))
    taxa_ps = set(search(Taxon, search_str, search_index='porterstemmer_index'))
    sightings_sw = set(search(Sighting, search_str, search_index='startswith_index'))
    sightings_ps = set(search(Sighting, search_str, search_index='porterstemmer_index'))

    return render_to_response('ias/search.html',
        {
            'taxa': taxa_sw | taxa_ps,
            'sightings': sightings_sw | sightings_ps
        },
        context_instance=RequestContext(request))
