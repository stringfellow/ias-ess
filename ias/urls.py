from django.conf.urls.defaults import *
from django.views.generic import ListView

from ias.models import Sighting


urlpatterns = patterns('',
    url('^sighting/$',
        'ias.views.sighting',
        name="ias-add-sighting",
    ),
    url('^taxon/register/$',
        'ias.views.taxon_register',
        name="ias-taxon-register"
    ),
    url('^taxon/registered/(?P<taxon_pk>\d+)/$',
        'ias.views.taxon_registered',
        name="ias-taxon-registered"
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
