__author__ = 'courtf'

from django.conf.urls import patterns, url
from game.views import game, turn

urlpatterns = patterns('',
    url(r'^(?P<game_id>\d+)/', game),
    url(r'^turn/(?P<turn_id>\d+)/', turn),
)

