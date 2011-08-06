from django.contrib import admin

from ias.models import Sighting, Taxon, TaxonExpert

admin.site.register(
    Taxon,
    list_display=('scientific_name', 'common_name', 'rank', 'active'),
#    search_fields=('scientific_name', 'common_name'),
)
admin.site.register(TaxonExpert)
admin.site.register(Sighting)
