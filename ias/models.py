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

    def __unicode__(self):
        return u'%s: %s' % (self.get_rank_display(), self.scientific_name)


class Sighting(models.Model):
    """An instance of some user seeing some thing."""
    taxon = models.ForeignKey(Taxon, related_name="sightings")
    email = models.EmailField(null=True, blank=True, help_text="You may add an "
        "email address if you wish...")
    contactable = models.BooleanField(default=True)
    lat = models.DecimalField(decimal_places=8, max_digits=11)
    lon = models.DecimalField(decimal_places=8, max_digits=11)
    photo = models.ForeignKey(Photo, related_name="sightings")


class Photo(models.Model):
    """An model to hold all the blobstore stuff."""
    photo = models.FileField()
    blob_key = models.CharField(max_length=256)
    url = models.CharField(max_length=256)

    def save(self, *args, **kwargs):
        if self.blob_key:
            blob_info = blobstore.BlobInfo.get(self.blob_key)
            blob_file_size = blob_info.size
            blob_type = blob_info.content_type

            blob_data = ''
            current = 0
            end = blobstore.MAX_BLOB_FETCH_SIZE - 1
            step = blobstore.MAX_BLOB_FETCH_SIZE - 1

            while current < blob_file_size:
                blob_data = ''.join([blob_data, blobstore.fetch_data(
                    self.blob_key, current, end)
                current = end + 1
                end += step

            img_obj = images_api.Image(image_data=blob_data)

            img_obj.rotate(360)
            img_obj.execute_transforms()
            self.url = images_api.get_serving_url(self.blob_key)
        super(Photo, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.blob_key:
            blobstore.delete(self.blob_key)
        super(Image, self).delete(*args, **kwargs)
    
    def get_absolute_url(self, size=0, crop=False):
        if size:
            url = ''.join([self.url, '=s', str(size)])
            if crop:
                url = '-'.join([url, 'c'])
            return url
        else:
            return self.url
