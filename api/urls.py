from django.conf.urls.defaults import *
from django.views.generic import ListView

from ias.models import Taxon

class JSONListView(ListView):
    def render_to_response(self, context, **kwargs):
        return super(JSONListView, self).render_to_response(context,
                        content_type='application/json', **kwargs)


urlpatterns = patterns('',
    url('^taxa/list$',
        JSONListView.as_view(
            model=Taxon,
            queryset=Taxon.actives.all(),
            template_name="api/taxon_list.html"),
        name='api-taxa-list'
    ),
    url('^sighting$',
        'api.views.sighting',
        name='api-sighting'
    ),
)
