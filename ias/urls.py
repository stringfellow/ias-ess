from django.conf.urls.defaults import *
from django.views.generic import ListView

from ias.models import Sighting


urlpatterns = patterns('',
    url('^sighting/$',
        'ias.views.sighting',
        name="ias-add-sighting",
    ),
    url('^taxon/register/$',
        'ias.views.register_taxon',
        name="ias-register-taxon"
    ),
    url('^sighting/(\d+)$',
        'ias.views.sighting_detail',
        name='ias-sighting-detail'
    ),
    url('^sightings/$',
        ListView.as_view(model=Sighting),
        name='ias-sighting-list'
    )
)
