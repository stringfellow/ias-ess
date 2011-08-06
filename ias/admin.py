from django.contrib import admin

from ias.models import Sighting, Taxon, TaxonExpert

admin.site.register(
    Taxon,
    list_display=('scientific_name', 'common_name', 'rank', 'active'),
#    search_fields=('scientific_name', 'common_name'),
)
admin.site.register(TaxonExpert)


def verify(modeladmin, request, queryset):
    queryset.update(verified=True)
verify.short_description = "Mark as verified"


admin.site.register(
    Sighting,
    list_display=('taxon', 'datetime', 'lat', 'lon', 'verified'),
    actions=[verify],
)
