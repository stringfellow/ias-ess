"""Models for IAS app - Species and Sightings."""
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

import tagging

from google.appengine.api import images as images_api
from google.appengine.api import files
from google.appengine.ext import blobstore


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
    questionnaire = models.CharField(
        max_length=100,
        help_text="Where is the Google Questionnaire to which users should "
        "fully answer their sighting."
    )
    active = models.BooleanField(default=False, help_text="Has this been OK'd?")
    style_name = models.CharField(max_length=30, null=True, blank=True)
    style_json = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u'%s: %s' % (self.get_rank_display(), self.scientific_name)

    def get_absolute_url(self):
        return reverse('ias-taxon-detail', args=[self.pk])
tagging.register(Taxon)


class TaxonExpert(models.Model):
    expert = models.ForeignKey(User)
    taxon = models.ForeignKey(Taxon)

    def __unicode__(self):
        return "%s for %s" % (
            self.taxon,
            self.expert)


class Photo(models.Model):
    """An model to hold all the blobstore stuff."""
    photo = models.FileField(upload_to="photo")
    blob_key = models.CharField(max_length=256)
    url = models.CharField(max_length=256)
    verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.blob_key:
            self.url = images_api.get_serving_url(self.blob_key)
        super(Photo, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.blob_key:
            blobstore.delete(self.blob_key)
        super(Photo, self).delete(*args, **kwargs)

    def get_absolute_url(self, size=0, crop=False):
        if size:
            url = ''.join([self.url, '=s', str(size)])
            if crop:
                url = '-'.join([url, 'c'])
            return url
        else:
            return self.url

    def __unicode__(self):
        return self.get_absolute_url()


class Sighting(models.Model):
    """An instance of some user seeing some thing."""
    taxon = models.ForeignKey(Taxon, related_name="sightings")
    email = models.EmailField(null=True, blank=True, help_text="You may add an "
        "email address if you wish...")
    contactable = models.BooleanField(default=True)
    datetime = models.DateTimeField(auto_now_add=True, default="06/07/2011 10:00:00")
    lat = models.DecimalField(decimal_places=8, max_digits=11)
    lon = models.DecimalField(decimal_places=8, max_digits=11)
    photo = models.ForeignKey(Photo, related_name="sightings", null=True, blank=True)
    has_completed_questionnaire = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('ias-sighting-detail', args=[self.pk])

    def __unicode__(self):
        return self.taxon.__unicode__()
