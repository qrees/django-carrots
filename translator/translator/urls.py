from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'translator.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^documents/', 'editor.views.document_list_view'),
    url(r'^document/(?P<name>.*)', 'editor.views.document_view')
)
