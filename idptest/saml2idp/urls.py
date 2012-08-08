from django.conf.urls.defaults import *
from views import descriptor, login_begin, login_init, login_process, logout
from django.conf import settings

urlpatterns = patterns('',
    # Single entry-point:
    #url( r'^init/(?P<resource>\w+)/(?P<target>.+)/$', login_init, name="login_init"),
    #url( r'^init/(?P<resource>\w+)/(?P<target>\w+)/$', login_init, name="login_init"),
    # Alternate init URL:
    #url( r'^init/(?P<resource>\w+)/(?P<target>\w+)/(?P<page>\w+)/$', login_init),
    url( r'^login/$', login_begin, name="login_begin"),
    url( r'^login/process/$', login_process, name='login_process'),
    url( r'^logout/$', logout, name="logout"),
    (r'^metadata/xml/$', descriptor),
)

# For backwards-compatibility:
urlpatterns += patterns('',
    url( r'^init/(?P<resource>\w+)/(?P<target>\w+)/$', login_init, name="login_init"),
)

#TODO: Build up new URLs based on new links from settings.SAML2IDP_REMOTES.
