__author__ = 'courtf'
from django.conf.urls import patterns, url
from views import player_dashboard, account_info

urlpatterns = patterns('',
    url(r'^/?$', player_dashboard),
    url(r'^dashboard/', player_dashboard),
    url(r'^account/', account_info),
)