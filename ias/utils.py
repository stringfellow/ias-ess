import re
from xml.etree import ElementTree as ET 
import urllib2

GOOGLE_QA_URL = "https://spreadsheets.google.com/spreadsheet/embeddedform?formkey="

def tweak_google_form(questionnaire_id, sighting_pk):
    url = GOOGLE_QA_URL + questionnaire_id
    response = urllib2.urlopen(url)
    data = response.read()
    data = re.sub(r'<br>', r'<br/>', data)
    data = re.sub(r'<input(.*?)>', r'<input\1/>', data)
    pat = re.compile(r'(<form.*?\/form>)', re.DOTALL)
    match = re.match(pat, data)
    if not match:
        import pdb
        pdb.set_trace()
    form = ET.fromstring(match.group(0))
    # find the input 0 - HOPE this is the ref...
    ref = form.find(".//input[@id='entry_0']")
    import pdb
    pdb.set_trace()
    ref['value'] = sighting_pk
    ref['type'] = 'hidden'
    # now extract its previous siblings
    sibs = []
    sib = ref.previousSibling
    sibs.append(sib)
    while sib.previousSibling != None:
        sib = sib.previousSibling
        sibs.append(sib)

    [s.extract() for s in sibs]

    # prepare form for our hackety redirect
    # see: http://www.morningcopy.com.au/tutorials/how-to-style-google-forms/
    form['target'] = "hidden_iframe"
    form['onsubmit'] = "submitted=true;"

    return form.prettify()
