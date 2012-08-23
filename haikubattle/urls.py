from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import dashboard.urls

admin.autodiscover()

import game.urls

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^game/', include(game.urls)),
    url(r'', include(dashboard.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login')
)
