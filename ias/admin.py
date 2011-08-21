from django.contrib import admin

from ias.models import Sighting, Taxon, TaxonExpert, Photo

admin.site.register(
    Taxon,
    list_display=('scientific_name', 'common_name', 'rank', 'active'),
#    search_fields=('scientific_name', 'common_name'),
)
admin.site.register(TaxonExpert)


class SightingAdmin(admin.ModelAdmin):
    
    list_display=('taxon', 'datetime', 'lat', 'lon', 'get_photo', 'verified')
    actions=['verify']

    def verify(self, request, queryset):
        queryset.update(verified=True)
    verify.short_description = "Mark as verified"

    def get_photo(self, obj):
        return "<img src='%s=s100' />" % (obj.photo.url)
    get_photo.short_description = 'Photo'
    get_photo.allow_tags = True


admin.site.register(Sighting, SightingAdmin)
admin.site.register(Photo)
