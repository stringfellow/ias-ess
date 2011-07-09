from django.conf.urls.defaults import *
from django.contrib import admin
import watercolours

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    #(r'^', include(admin.site.urls)),
    (r'^admin/', include(admin.site.urls)),
    url(r'^images/list/$', 'watercolours.views.list_images', name="images"),
    url('^get_image/$', 'watercolours.views.get_image', name='get_image'),
    url('^$', 'django.views.generic.simple.direct_to_template',
     {'template': 'home.html'}, name="home"),
)

