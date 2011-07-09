from django.conf.urls.defaults import *



urlpatterns = patterns('',
    ('^sighting/$',
     'ias.views.sighting',
     ),
    ('^taxon/register/$',
        'views.register_taxon',
        name="register_species")
)
