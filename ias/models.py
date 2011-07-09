"""Models for IAS app - Species and Sightings."""
from django.db import models


TAXA_CHOICES = (
    ('SPECIES', 'Species'),
    ('GENUS', 'Genus'),
    ('FAMILY', 'Family'),
    ('ORDER', 'Order'),
    ('CLASS', 'Class'),
    ('PHYLUM', 'Phylum'),
    ('KINGDOM', 'Kingdom'),
    ('DOMAIN', 'Domain'),
)

class Taxon(models.Model):
    """A thing to sight, could be a group or a single species."""
    scientific_name = models.CharField(max_length=200)
    rank = models.CharField(choices=TAXA_CHOICES, max_length=50)
    key_text = models.TextField(help_text="A helpful description so that users"
        " can identify this taxon easily.")
    questionnaire = models.URLField(help_text="Where is the Google"
        " Questionnaire to which users should fully answer their sighting.")



