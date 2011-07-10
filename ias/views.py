from __future__ import with_statement
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.template import RequestContext

from google.appengine.api import images as images_api
from google.appengine.api import files
from google.appengine.ext import blobstore

from ias.models import Photo, Sighting, Taxon, TaxonExpert
from ias.forms import SightingForm, RegisterTaxonForm


def sighting(request):
    """A user sees a thing, record it."""
    if request.method == 'POST':
        form = SightingForm(request.POST, request.FILES)
        if form.is_valid():
            sighting = form.save(commit=False)
            photo_file = request.FILES['photo']
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
            photo_obj.save()
            sighting.photo = photo_obj
            sighting.save()
            return HttpResponseRedirect(reverse(
                'ias-sighting-detail',
                args=[sighting.pk])
            )
    else:
        form = SightingForm()
    return render_to_response(
        'ias/sighting.html',
        {'form': form,
         # action="." does not work with jQuery mobile as it does not
         # call the URL with a slash on the end which then causes a
         # Django error
         'action': reverse('ias-add-sighting')
         }
    )

@login_required
def taxon_register(request):
    """The start of flow for registering a new taxon."""
    if request.method == 'POST':
        form = RegisterTaxonForm(request.POST)
        if form.is_valid():
            taxon = form.save()
            TaxonExpert.objects.create(expert=request.user, taxon=taxon)
            return HttpResponseRedirect(reverse(
                'ias-taxon-registered',
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


def taxon_registered(request, taxon_pk):
    """Show taxa..."""

    taxon = get_object_or_404(Taxon, pk=taxon_pk)
    taxon_experts = TaxonExpert.objects.filter(taxon=taxon)
    experts = User.objects.filter(pk__in=taxon_experts)

    return render_to_response(
        'ias/taxon_registered.html',
        {
            'taxon': taxon,
            'experts': experts,
        },
        context_instance=RequestContext(request))


def sighting_detail(request, pk):
    if pk:
        sighting = Sighting.objects.get(pk=pk)
        return render_to_response(
            'ias/sighting_detail.html',
            {'sighting': sighting}
            )
    return HttpResponseRedirect(reverse('ias-add-sighting'))

