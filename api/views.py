import logging

from django.http import HttpResponse

from ias.forms import SightingForm


def sighting(request):
    if request.method == 'POST':
        logging.debug("POST!")
        logging.debug(request.POST)
        logging.debug(request.FILES)
        form = SightingForm(request.POST, request.FILES)
        if form.is_valid():
            logging.debug("VALID"*10)
        else:
            logging.error(form.errors)
    else:
        logging.debug(request)
    return HttpResponse("OK")
