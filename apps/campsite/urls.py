from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.registration), #submits the registration, creating a new user
    url(r'^login$', views.login), #submits the login
    url(r'^new_user/(?P<id>\d+)$', views.success), #renders the success page
    url(r'^logout$', views.logout), #clears session and redirects to login page
]