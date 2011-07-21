import logging

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_view_exempt

from ias.forms import SightingForm


@csrf_view_exempt
def sighting(request):
    if request.method == 'POST':
        logging.debug("POST!")
        logging.debug(request.POST)
        logging.debug(request.FILES)
        form = SightingForm(request.POST, request.FILES)
        if form.is_valid():
            logging.debug("VALID"*10)
            sighting = form.save()
            return HttpResponse("http://localhost:8080"+reverse(
                "ias-sighting-detail", args=[sighting.pk]))
        else:
            logging.error(form.errors)
    else:
        logging.debug(request)
    return HttpResponse("OK")
