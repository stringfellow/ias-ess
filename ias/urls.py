from django.conf.urls.defaults import *

urlpatterns = patterns('',
    ('^sighting/$',
     'ias.views.sighting',
     ),
)
