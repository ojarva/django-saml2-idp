from django.conf.urls.defaults import *
from views import login, login_begin, login_post, login_process, login_continue, logout

urlpatterns = patterns('',
   url( r'^login/$', login, name="login"),
   url( r'^login/begin/$', login_begin, name="login_begin"),
   url( r'^login/post/$', login_post, name="login_post"),
   url( r'^login/process/$', login_process, name='login_process'),
   url( r'^login/continue/$', login_continue, name='login_continue'),
   url( r'^logout/$', logout, name="logout"),
)
