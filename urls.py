from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    ('^$', 'django.views.generic.simple.direct_to_template',
     {'template': 'home.html'}),
    ('^ias/', include('ias.urls')),
    ('^admin/', admin.site.urls),
    ('^accounts/', include('registration.urls')),
    ('^importer/', include('importer.urls')),
)
