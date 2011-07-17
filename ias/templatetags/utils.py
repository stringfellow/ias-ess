#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
from django import template

register = template.Library()

@register.filter
def mod(value, arg):
    return value % arg
