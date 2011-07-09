from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
import logging

from ias.forms import SightingForm


def sighting(request):
    if request.method == 'POST':
        form = SightingForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            file = request.FILES['photo']
            size = file.size
            type = file.content_type
            image = blobstore.create(
                mime_type=type, _blobinfo_uploaded_filename=file.name)

            with files.open(image, 'a') as f:
                data = file.read(blobstore.MAX_BLOB_FETCH_SIZE)
                    f.write(data)
                    data = file.read(blobstore.MAX_BLOB_FETCH_SIZE)

            files.finalse(image)
            obj.blob_key = files.blobstore.get_blob_key(image)
            obj.photo = None
            obj.save()
            return HttpResponseRedirect(reverse('ias-sighting-thanks'))
    else:
        form = SightingForm()
    return render_to_response(
        'ias/sighting.html',
        {'form': form}
    )
