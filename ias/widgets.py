#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
from django import forms
from django.template import loader, Context

class GoogleLatLon(forms.TextInput):
    """Render a map and know which companion fields to fill out."""

    class Media:
        js = ['http://maps.googleapis.com/maps/api/js?sensor=true']

    def __init__(self, lat_name='lat', lon_name='lon', attrs=None):
        self.lat_name = lat_name
        self.lon_name = lon_name
        super(GoogleLatLon, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        map_template = "ias/widgets/google_lat_lon.html"
        t = loader.get_template(map_template)
        return t.render(Context({
            'lat_name': self.lat_name,
            'lon_name': self.lon_name,
            'attrs': attrs,
        }))
