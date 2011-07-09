from django.conf.urls.defaults import *

urlpatterns = patterns('',
    ('^sighting/$',
     'django.views.generic.simple.direct_to_template',
     {'template': 'ias/sighting.html'}
     ),
)
