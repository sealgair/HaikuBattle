from django.conf.urls import patterns, url
from friends.views import add_friend, confirm_friend

urlpatterns = patterns('',
    url(r'^add/', add_friend),
    url(r'^confirm/', confirm_friend),
)

