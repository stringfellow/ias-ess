from django.contrib import admin

from ias.models import Sighting, Taxon

admin.site.register(Taxon)
admin.site.register(Sighting)
