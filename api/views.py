from __future__ import with_statement

import logging
import datetime

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_view_exempt
from django.contrib.sites.models import Site

from ias.forms import SightingForm
from ias.utils import save_photo


# Just a constant to say we are in an app.
IN_APP = 'inApp'

@csrf_view_exempt
def sighting(request):
    if request.method == 'POST':
        form = SightingForm(request.POST, request.FILES)
        if form.is_valid():
            sighting = form.save(commit=False)
            photo_obj = save_photo(request.FILES['image'])
            sighting.photo = photo_obj
            sighting.datetime = datetime.datetime.now()
            sighting.save()
            url = [
                "http://",
                Site.objects.all()[0].domain,
                reverse("ias-sighting-detail", args=[sighting.pk, IN_APP]),
                "#Questionnaire"
            ]
            return HttpResponse("".join(url))
        else:
            logging.error("POST: %s, ERROR: %s" % (request.POST, form.errors))
    else:
        logging.debug(request)
    return HttpResponse("OK")
