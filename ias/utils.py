from BeautifulSoup import BeautifulSoup
import urllib2

GOOGLE_QA_URL = "https://spreadsheets.google.com/spreadsheet/viewform?formkey="

def tweak_google_form(questionnaire_id, sighting_pk):
    url = GOOGLE_QA_URL + questionnaire_id
    response = urllib2.urlopen(url)
    data = response.read()

    soup = BeautifulSoup(data)
    # find the form
    form = soup.find('form')
    # find the input 0 - HOPE this is the ref...
    ref = form.find('input', id='entry_0')
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

    return form.prettify()
