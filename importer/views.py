import cgi
import os
import logging

import gdata.auth
import gdata.spreadsheets.client
import gdata.spreadsheets.data
import gdata.docs.client
import gdata.docs.data

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from google.appengine.api import users

CONSUMER_KEY = 'anonymous'
CONSUMER_SECRET = 'anonymous'
SCOPES = ['https://spreadsheets.google.com/feeds/',
          'https://docs.google.com/feeds/',
          ]
REQUEST_TOKEN = 'RequestToken'
ACCESS_TOKEN = 'AccessToken'

#client = gdata.spreadsheets.client.SpreadsheetsClient()
client = gdata.docs.client.DocsClient()


def main_page(request):
  if not users.get_current_user():
    return HttpResponseRedirect(users.create_login_url(request.build_absolute_uri()))

  access_token = gdata.gauth.AeLoad(ACCESS_TOKEN)
  if not isinstance(access_token, gdata.gauth.OAuthHmacToken):
    return HttpResponseRedirect('/importer/get_oauth_token')

  return render_to_response('index.html', {})


def get_oauth_token(request):
  """Fetches a request token and redirects the user to the approval page."""

  if users.get_current_user():
    # 1.) REQUEST TOKEN STEP. Provide the data scope(s) and the page we'll
    # be redirected back to after the user grants access on the approval page.
    oauth_callback_url = 'http://%s:%s/importer/get_access_token' % (request.META.get('SERVER_NAME'), request.META.get('SERVER_PORT'))
    request_token = client.GetOAuthToken(SCOPES, oauth_callback_url, CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)

    # When using HMAC, persist the token secret in order to re-create an
    # OAuthToken object coming back from the approval page.
    gdata.gauth.AeSave(request_token, REQUEST_TOKEN)

    # Generate the URL to redirect the user to.
    authorization_url = request_token.generate_authorization_url()

    # 2.) APPROVAL STEP.  Redirect to user to Google's OAuth approval page.
    return HttpResponseRedirect(authorization_url)

def get_access_token(request):
  """This handler is responsible for fetching an initial OAuth request token,
  redirecting the user to the approval page.  When the user grants access, they
  will be redirected back to this GET handler and their authorized request token
  will be exchanged for a long-lived access token."""
  saved_request_token = gdata.gauth.AeLoad(REQUEST_TOKEN)
  request_token = gdata.gauth.AuthorizeRequestToken(saved_request_token,
                                                      request.build_absolute_uri())

  # 3.) Exchange the authorized request token for an access token
  access_token = client.GetAccessToken(request_token)
  gdata.gauth.AeSave(access_token, ACCESS_TOKEN)

  return HttpResponseRedirect('/importer/')

def setup_token():
  access_token = gdata.gauth.AeLoad(ACCESS_TOKEN)
  client.auth_token = gdata.gauth.OAuthHmacToken(
      CONSUMER_KEY, CONSUMER_SECRET,
      access_token.token, access_token.token_secret,
      gdata.gauth.ACCESS_TOKEN,
      next=None, verifier=None)
  client.auth_token = access_token

def import_spreadsheet(request):
  import re
  import models

  setup_token()

  # Figure out what spreadsheet to import
  spreadsheet = request.GET.get('spreadsheet', '0Ar7e9bY7dwnBdEIzUk5kSk5CZ0kyYXVrempkWW80Snc')
  # If they entered a URL, extract the key
  if spreadsheet.find('google.com') > -1:
    spreadsheet_key = re.search('key=([^(?|&)]*)', spreadsheet).group(1)
  else:
    spreadsheet_key = spreadsheet

  # We're assuming first worksheet for convenience
  worksheet_id = 'od6'

  # Retrieve the "values" projection of the list feed, the most DB-like feed
  list_feed = 'https://spreadsheets.google.com/feeds/list/%s/%s/private/values' % (spreadsheet_key, worksheet_id)
  feed = client.get_feed(list_feed,
                         desired_class=gdata.spreadsheets.data.ListsFeed)

  # For each row, save it as a datastore entity
  sheet = ''
  for row in feed.entry:
    sheet += unicode(row)
    # firstname = row.get_value('firstname')
    # lastname = row.get_value('lastname')
    # email = row.get_value('email')
    # person = models.Person(firstname=firstname, lastname=lastname, email=email)
    # person.save()

  #return HttpResponse('Saved %s rows' % str(len(feed.entry)))
  return HttpResponse(sheet)

def copy_spreadsheet(request):
  setup_token()
  
  doc_feed = 'https://docs.google.com/feeds/default/private/full/'
  feed = client.get_feed(doc_feed, desired_class=gdata.docs.data.DocList)
  
  docs = []
  for doc in feed.entry:
    docs.append(doc.title.text)

  return HttpResponse('\n'.join(docs), mimetype="text/plain")
