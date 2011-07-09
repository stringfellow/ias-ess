from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

from ias.forms import SightingForm


def sighting(request):
    if request.method == 'POST':
        form = SightingForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('ias-sighting-thanks'))
    else:
        form = SightingForm()
    return render_to_response(
        'ias/sighting.html',
        {'form': form}
    )
