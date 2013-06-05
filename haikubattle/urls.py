from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import dashboard.urls
import djanrain.urls

admin.autodiscover()

import game.urls
import friends.urls

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^game/', include(game.urls)),
    url(r'^friends/', include(friends.urls)),
    url(r'', include(dashboard.urls)),
    url(r'^auth/', include(djanrain.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/', include('registration.backends.default.urls')),
)
