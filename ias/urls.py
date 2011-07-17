from django.conf.urls.defaults import *
from django.views.generic import ListView

from ias.models import Sighting, Taxon


urlpatterns = patterns('',
    url('^sighting/$',
        ListView.as_view(model=Sighting),
        name='ias-sighting-list'
    ),
    url('^sighting/add/$',
        'ias.views.sighting_add',
        name="ias-sighting-add",
    ),
    url('^sighting/(\d+)$',
        'ias.views.sighting_detail',
        name='ias-sighting-detail'
    ),
    url('^taxon/$',
        ListView.as_view(model=Taxon),
        name="ias-taxon-list"
    ),
    url('^taxon/add/$',
        'ias.views.taxon_add',
        name="ias-taxon-add"
    ),
    url('^taxon/(\d+)/$',
        'ias.views.taxon_detail',
        name="ias-taxon-detail"
    ),
    url('^map/$',
        'ias.views.map',
        name="ias-map"
    ),
)
