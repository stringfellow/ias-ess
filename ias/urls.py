from django.conf.urls.defaults import *
from django.views.generic import ListView

from ias.models import Sighting, Taxon


urlpatterns = patterns('',
    url('^sighting/$',
        ListView.as_view(
            model=Sighting,
            queryset=Sighting.objects.filter(verified=True)
        ),
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
    # URL for mobile redirect
    url('^sighting/(\d+)/(inApp)$',
        'ias.views.sighting_detail',
        name='ias-sighting-detail'
    ),
    url('^taxon/$',
        ListView.as_view(model=Taxon, queryset=Taxon.actives.all()),
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
    url('^map/get_data/$',
        'ias.views.map_data',
        name="ias-map-data"
    ),
    url(r'^search/', 'ias.views.search_db', name='search-db'),
    url(r'^resave/', 'ias.views.resave', name='resave'),
)
