from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^documents/', 'editor.views.document_list_view'),
    url(r'^document/(?P<name>.*)', 'editor.views.document_view'),
    url(r'^set_valid.json', 'editor.views.set_valid'),
)
