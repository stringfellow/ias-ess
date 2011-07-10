from django.conf.urls.defaults import *


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
    )
)
