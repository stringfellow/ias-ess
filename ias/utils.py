import elementtree.ElementTree as ET
import urllib2

GOOGLE_QA_URL = "https://spreadsheets.google.com/spreadsheet/viewform?formkey="

def get_google_form(questionnaire_id):
    url = GOOGLE_QA_URL + questionnaire_id
    response = urllib2.urlopen(url)

    import pdb
    pdb.set_trace()

