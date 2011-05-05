# -*- coding: utf-8 -*-
import os

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from . import settings

urlpatterns = patterns('',
    ('^$|^index$', 'views.index'),
    
    ('^ajax/search/title', 'views.ajax_search_title'),
    
    ('^ajax/search/fansub', 'views.ajax_search_fansub'),
    
    ('^ajax/packages/add', 'views.ajax_add_packages'),
    
    ('^(anime|dorama|manga)/rls/(add|edit)/?(|\d+)', 'views.edit_release'),
    
    ('^(anime|dorama|manga)/(add|edit)/?(|\d+)', 'views.edit_title'),
    
    # En uso para la versión de desarrollo, desactivar
    # en el proyecto final
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(settings.PROJECT_PATH, 'static'),
         'show_indexes': True}),
         
    # Example:
    # (r'^hikkea/', include('hikkea.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
