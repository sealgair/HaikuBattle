__author__ = 'courtf'

from django.conf.urls import patterns, url

urlpatterns = patterns('game.views',
    url(r'^(?P<game_id>\d+)/', 'game'),
    url(r'^play_random/(?P<game_id>\d+)/', 'play_random'),
    url(r'^next_hotseat/(?P<game_id>\d+)/', 'next_hotseat_player'),
    url(r'^next_hotseat/(?P<game_id>\d+)/(?P<user_id>\d+)/', 'next_hotseat_player'),
    url(r'^invite/(?P<game_id>\d+)/', 'invite'),
    url(r'^quit/(?P<game_id>\d+)/', 'quit'),
    url(r'^turn/(?P<turn_id>\d+)/', 'turn'),
    url(r'^add_hotseat_player/(?P<game_id>\d+)/', 'add_hotseat_player'),
    url(r'^remove_hotseat_player/(?P<game_id>\d+)/(?P<user_id>\d+)/', 'remove_hotseat_player'),
    url(r'^random_haiku/', 'random_haiku'),
    url(r'^random_haiku.json', 'random_haiku', kwargs={'format': 'json'}),
)

