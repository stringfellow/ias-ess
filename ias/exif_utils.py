#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import datetime
import time

from EXIF import process_file

	
def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    values = value.values

    d0 = values[0].num
    d1 = values[0].den
    d = float(d0) / float(d1)
    
    m0 = values[1].num
    m1 = values[1].den
    m = float(m0) / float(m1)

    s0 = values[2].num
    s1 = values[2].den
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def get_lat_lon(exif):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None

    if len(filter(lambda k: str(k).startswith('GPS'), exif.keys())):
        gps_latitude = exif["GPS GPSLatitude"]
        gps_latitude_ref = exif["GPS GPSLatitudeRef"]
        gps_longitude = exif["GPS GPSLongitude"]
        gps_longitude_ref = exif["GPS GPSLongitudeRef"]

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref.values != "N":
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref.values != "E":
                lon = 0 - lon

    return lat, lon


def get_datetime(exif):
    """Get the timestamp from the photo if possible."""
    if 'Image DateTime' in exif:
        time_format = "%Y:%m:%d %H:%M:%S"
        dt = datetime.datetime.fromtimestamp(
            time.mktime(time.strptime(
                str(exif['Image DateTime']),
                time_format)))
        return dt
    else:
        return datetime.datetime.now()
