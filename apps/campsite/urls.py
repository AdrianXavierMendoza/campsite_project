from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'login_page$', views.login_page), #renders login page
    url(r'^register$', views.registration), #submits the registration, creating a new user
    url(r'^login$', views.login), #submits the login
    url(r'^new_user$', views.success), #renders the success page
    url(r'^logout$', views.logout), #clears session and redirects to login page
    url(r'^profile$', views.profile), #renders user profile
    url(r'^search$', views.search), #renders search page
    url(r'^reservation$', views.reservation), #renders reservation page
    url(r'^edit$', views.edit), #renders edit page
    url(r'^confirmation$',views.confirmation), #renders confirmation page 

]