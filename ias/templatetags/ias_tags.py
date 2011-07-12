from django import template

register = template.Library()

@register.filter
def crop(photo):
    if photo:
        return photo.get_absolute_url(crop=True)

@register.filter
def size(photo, arg):
    if photo:
        return photo.get_absolute_url(size=arg)

@register.filter
def is_expert_for(user, sighting):
    return user in [te.expert for te in sighting.taxon.taxonexpert_set.all()]
