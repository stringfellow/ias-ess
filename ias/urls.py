from django.conf.urls.defaults import *


urlpatterns = patterns('',
    url('^sighting/$',
     'ias.views.sighting',
     name='ias-add-sighting'
    ),
    url('^sighting/(\d+)$',
        'ias.views.sighting_detail',
        name='ias-sighting-detail'
    ),
    #url('^taxon/register/$',
    #    'ias.views.register_taxon',
    #    name="register_species")
)
