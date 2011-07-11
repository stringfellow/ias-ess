import re
import logging
from xml.etree import ElementTree as ET 
import urllib2

GOOGLE_QA_URL = "https://spreadsheets.google.com/spreadsheet/embeddedform?formkey="

def tweak_google_form(questionnaire_id, sighting_pk):
    url = GOOGLE_QA_URL + questionnaire_id
    response = urllib2.urlopen(url)
    data = response.read()
    data = data.replace('>', '>\n')  # why? Who knows!
    data = re.sub(r'<br>', r'<br/>', data)
    data = re.sub(r'<input(.*?)>', r'<input\1/>', data)
    pat = re.compile(r'(<form.*?\/form>)', re.DOTALL)
    match = re.search(pat, data)
    if not match:
        logging.warn("Form failed to match regex for key %s" % (
            questionnaire_id))
        return ""
    form = ET.fromstring(match.group(0))
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
