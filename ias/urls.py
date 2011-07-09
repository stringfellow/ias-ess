from django.conf.urls.defaults import *


urlpatterns = patterns('',
    ('^sighting/$',
     'ias.views.sighting',
     ),
    url('^sighting/done/$',
        'django.views.generic.simple.direct_to_template',
        {'template': 'ias/sighting_done.html'},
        name="ias-sighting-thanks",
    ),
    url('^taxon/register/$',
        'views.register_taxon',
        name="register_species")
)
