from django.conf.urls import url
from auth import views

urlpatterns = [
    url(r'^logout/$', views.logout_user, name = 'logout'),
]
