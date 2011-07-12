from django.contrib import admin

from ias.models import Sighting, Taxon, TaxonExpert

admin.site.register(Taxon)
admin.site.register(TaxonExpert)
admin.site.register(Sighting)
