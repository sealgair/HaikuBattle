__author__ = 'courtf'
from django.conf.urls import patterns, url
from views import player_dashboard

urlpatterns = patterns('',
    url(r'^dashboard/', player_dashboard),
)