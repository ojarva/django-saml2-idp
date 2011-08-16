from django.conf.urls.defaults import *
from views import login, logout, logged_out

urlpatterns = patterns('',
   url( r'^login/$', login, name="saml2_idp_login"),
   url('^logout/$', logout, name="saml2_idp_logout"),
   url('^logged_out/$', logged_out, name="saml2_idp_logged_out"),
)
