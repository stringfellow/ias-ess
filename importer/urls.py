from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^get_oauth_token', 'importer.views.get_oauth_token'),
    (r'^get_access_token', 'importer.views.get_access_token'),
    (r'^import_spreadsheet', 'importer.views.import_spreadsheet'),
    (r'^copy_spreadsheet', 'importer.views.copy_spreadsheet'),
    (r'^get_data/(?P<key>[^/]*)/(?P<sheet>[^/]*/)', 'importer.views.get_data_from_sheet'),
    (r'^get_data/(?P<key>[^/]*)/', 'importer.views.get_data_from_sheet'),
    (r'^$', 'importer.views.main_page'),
)
