from django import template

register = template.Library()

@register.filter
def crop(photo):
    return photo.get_absolute_url(crop=True)

@register.filter
def size(photo, arg):
    return photo.get_absolute_url(size=arg)
