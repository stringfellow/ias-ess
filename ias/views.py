from django.shortcuts import render_to_response

from ias.forms import SightingForm


def sighting(request):
    if request.method == 'POST':
        form = SightingForm(request.POST)
        if form.is_valid():
            raise NotImplementedError
    else:
        form = SightingForm()
    return render_to_response(
        'ias/sighting.html',
        {'form': form}
    )
