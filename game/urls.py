__author__ = 'courtf'

from django.conf.urls import patterns, url
from game.views import game, turn, invite, quit, add_hotseat_player, remove_hotseat_player, next_hotseat_player

urlpatterns = patterns('',
    url(r'^(?P<game_id>\d+)/', game),
    url(r'^next_hotseat/(?P<game_id>\d+)/', next_hotseat_player),
    url(r'^next_hotseat/(?P<game_id>\d+)/(?P<user_id>\d+)/', next_hotseat_player),
    url(r'^invite/(?P<game_id>\d+)/', invite),
    url(r'^quit/(?P<game_id>\d+)/', quit),
    url(r'^turn/(?P<turn_id>\d+)/', turn),
    url(r'^add_hotseat_player/(?P<game_id>\d+)/', add_hotseat_player),
    url(r'^remove_hotseat_player/(?P<game_id>\d+)/(?P<user_id>\d+)/', remove_hotseat_player),
)

