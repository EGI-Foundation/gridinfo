from django.conf.urls.defaults import *
import settings
from os import path as os_path
from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
    (r'^$', 'core.views.initial'),
    (r'^gstat/about$', 'core.views.about'),
    (r'^about$', 'core.views.about'),
    (r'^gstat/register$', 'core.views.register'),
    (r'^register$', 'core.views.register'),
    (r'^gstat/core/filter$', 'core.views.filter'),
    (r'^core/filter$', 'core.views.filter'),
    (r'^gstat/core/filter/(?P<type>\w+)$', 'core.views.filter'),
    (r'^core/filter/(?P<type>\w+)$', 'core.views.filter'),
    (r'^gstat$', include('core.urls')),
    (r'^gstat/', include('core.urls')),
    (r'^summary$', redirect_to, {'url': '/gstat/summary/'}),
    (r'^summary/', include('summary.urls')),
    (r'^gridmap$', redirect_to, {'url': '/gstat/gridmap/'}),
    (r'^gridmap/', include('gridmap.urls')),
    (r'^site$', include('gridsite.urls')),
    (r'^site/', include('gridsite.urls')),
    (r'^service$', include('service.urls')),
    (r'^service/', include('service.urls')),
    (r'^geo$', include('geo.urls')),
    (r'^geo/', include('geo.urls')),
    (r'^ldap$', include('ldapbrowser.urls')),
    (r'^ldap/', include('ldapbrowser.urls')),
    (r'^vo$', include('vo.urls')),
    (r'^vo/', include('vo.urls')),
    (r'^rrd/', include('rrd.urls')),
    (r'^media/(.*)', 'django.views.static.serve', {'document_root': os_path.join(settings.PROJECT_PATH, 'media')}),
)
