from django.contrib import admin

from ias.models import Sighting, Taxon, TaxonExpert, Photo

admin.site.register(
    Taxon,
    list_display=('scientific_name', 'common_name', 'rank', 'active'),
#    search_fields=('scientific_name', 'common_name'),
)
admin.site.register(TaxonExpert)


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('url', 'get_photo')

    def get_photo(self, obj):
        gae_url = "https://appengine.google.com/blobstore/detail?app_id=s~ias-ess&key="
        return "<a href='%s%s' target='_blank'><img src='%s=s100' /></a>" % (
            gae_url, obj.blob_key, obj.url)
    get_photo.short_description = 'Photo'
    get_photo.allow_tags = True

class SightingAdmin(admin.ModelAdmin):
    
    list_display=('taxon', 'datetime', 'lat', 'lon', 'get_photo', 'verified')
    actions=['verify']

    def verify(self, request, queryset):
        queryset.update(verified=True)
    verify.short_description = "Mark as verified"

    def get_photo(self, obj):
        gae_url = "https://appengine.google.com/blobstore/detail?app_id=s~ias-ess&key="
        return "<a href='%s%s' target='_blank'><img src='%s=s100' /></a>" % (
            gae_url, obj.photo.blob_key, obj.photo.url)
    get_photo.short_description = 'Photo'
    get_photo.allow_tags = True


admin.site.register(Sighting, SightingAdmin)
admin.site.register(Photo, PhotoAdmin)
