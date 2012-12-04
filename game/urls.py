__author__ = 'courtf'

from django.conf.urls import patterns, url
from game.views import game, turn, invite, quit

urlpatterns = patterns('',
    url(r'^(?P<game_id>\d+)/', game),
    url(r'^(?P<game_id>\d+)/', game),
    url(r'^invite/(?P<game_id>\d+)/', invite),
    url(r'^quit/(?P<game_id>\d+)/', quit),
    url(r'^turn/(?P<turn_id>\d+)/', turn),
)

