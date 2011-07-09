from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

from ias.forms import SightingForm


def sighting(request):
    """A user sees a thing, record it."""
    if request.method == 'POST':
        form = SightingForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('ias-sighting-thanks'))
    else:
        form = SightingForm()
    return render_to_response(
        'ias/sighting.html',
        {'form': form,
         # action="." does not work with jQuery mobile as it does not
         # call the URL with a slash on the end which then causes a
         # Django error
         'action': reverse('ias-sighting')
         }
    )


def register_species(request):
    """The start of flow for registering a new taxon."""
    pass

