from django.conf.urls.defaults import *

urlpatterns = patterns('ldapbrowser.views',
    (r'^$', 'index'),
    (r'^browse', 'browse'),
)
