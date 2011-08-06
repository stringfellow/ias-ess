from django import template
from django.utils.safestring import mark_safe

from ias.models import Taxon, Sighting

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

@register.filter
def info(object):
    if object:
        string = '<br /><br />'
        for prop in object.__dict__:
            if not prop.startswith('_'):
                dictstring = '<b>%s</b> : %s' % (prop, repr(object.__dict__[prop]))
                string = '<br />'.join([string, dictstring])
        return mark_safe(string)
info.is_safe = True

class TaxaListNode(template.Node):
    def __init__(self, number, var_name):
        self.number = number
        self.var_name = var_name

    def render(self, context):
        taxa = Taxon.actives.all()
        if Taxon.objects.count() > int(self.number):
            taxa = taxa[:self.number]
        context[self.var_name] = taxa
        return ''

import re
@register.tag
def taxa_list(parser, token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    number, var_name = m.groups()
    if not (number[0] == number[-1] and number[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return TaxaListNode(number[1:-1], var_name)


class SightingListNode(template.Node):
    def __init__(self, number, var_name):
        self.number = number
        self.var_name = var_name

    def render(self, context):
        sightings = Sighting.objects.filter(verified=True)
        if sightings.count() > int(self.number):
            sightings = sightings[:self.number]
        context[self.var_name] = sightings
        return ''

@register.tag
def sightings_list(parser, token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'(.*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    number, var_name = m.groups()
    if not (number[0] == number[-1] and number[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return SightingListNode(number[1:-1], var_name)
