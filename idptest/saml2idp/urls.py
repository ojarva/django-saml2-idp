from django.conf.urls.defaults import *
from views import landing, logged_in, logout, logged_out

urlpatterns = patterns('',
   url( r'^login/$', landing, name="saml2_idp_landing"),
   url('^login/continue/$', logged_in, name="saml2_idp_login_continue"),
   url('^logout/$', logout, name="saml2_idp_logout"),
   url('^logged_out/$', logged_in, name="saml2_idp_logged_out"),
)
