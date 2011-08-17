from django.conf.urls.defaults import *
from views import login, logout

urlpatterns = patterns('',
   url( r'^login/$', login, name="saml2_idp_login"),
   url('^logout/$', logout, name="saml2_idp_logout"),
)
