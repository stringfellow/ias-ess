from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^get_oauth_token', 'importer.views.get_oauth_token'),
  (r'^get_access_token', 'importer.views.get_access_token'),
  (r'^import_spreadsheet', 'importer.views.import_spreadsheet'),
  (r'^copy_spreadsheet', 'importer.views.copy_spreadsheet'),
  (r'^$', 'importer.views.main_page'),
)
