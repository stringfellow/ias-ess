from __future__ import with_statement

import re
import time
import logging
import urllib2
from xml.etree import ElementTree as ET 

from google.appengine.api import images as images_api
from google.appengine.api import files
from google.appengine.ext import blobstore

import ias

#from set_trace import set_trace

GOOGLE_QA_URL = "https://spreadsheets.google.com/spreadsheet/embeddedform?formkey="

def save_photo(image):
    photo_file = image
    photo_file.seek(0)
    photo_size = photo_file.size
    photo_type = photo_file.content_type
    photo_store = files.blobstore.create(
        mime_type=photo_type,
        _blobinfo_uploaded_filename=photo_file.name)

    with files.open(photo_store, 'a') as f:
        data = photo_file.read(blobstore.MAX_BLOB_FETCH_SIZE)
        while data:
            f.write(data)
            data = photo_file.read(blobstore.MAX_BLOB_FETCH_SIZE)

    files.finalize(photo_store)
    photo_obj = ias.models.Photo()
    photo_obj.photo = None

    # seems like sometimes the finalization is not fast enough or 
    # perhaps doesn't block until it is finished. This is a horrid
    # but effective way to make sure we get the blob key
    # I'm sure there is a better way, expect finalize emits something?
    timeout = 0
    while photo_obj.blob_key == None and timeout < 30:
        timeout += 1
        time.sleep(0.5)
        photo_obj.blob_key = files.blobstore.get_blob_key(photo_store)
    photo_obj.verified = False
    photo_obj.save()
    return photo_obj


def tweak_google_form(questionnaire_id, sighting_pk):
    url = GOOGLE_QA_URL + questionnaire_id
    response = urllib2.urlopen(url)
    data = response.read()
    data = data.replace('>', '>\n')  # why? Who knows!
    data = re.sub(r'<br>', r'<br/>', data)
    data = re.sub(r'<input(.*?)>', r'<input\1/>', data)
    data = re.sub(r'<input(.*?) checked (.*?)>', r'<input\1 \2>', data)
    pat = re.compile(r'(<form.*?\/form>)', re.DOTALL)
    match = re.search(pat, data)
    if not match:
        logging.warn("Form failed to match regex for key %s" % (
            questionnaire_id))
        return ""
    lines = filter(lambda(x): len(x), match.group(0).split('\n'))
    html = '\n'.join(lines)
    # set_trace()
    form = ET.fromstring(html)
    
    # find the input 0 - HOPE this is the ref...
    ref_div = form.find(".//div")
    # brute force hide the div with the labels in it
    ref_div.set('style', 'display: none;')
    # and set the input to hidden...
    ref = form.find(".//input")
    ref.set('type', 'hidden')
    ref.set('value', str(sighting_pk))
    # now extract its previous siblings
#    sibs = []
#    sib = ref.previousSibling
#    sibs.append(sib)
#    while sib.previousSibling != None:
#        sib = sib.previousSibling
#        sibs.append(sib)
#
#    [s.extract() for s in sibs]

    # prepare form for our hackety redirect
    # see: http://www.morningcopy.com.au/tutorials/how-to-style-google-forms/
    form.set('target', "hidden_iframe")
    form.set('onsubmit', "submitted=true;")

    return ET.tostring(form)
