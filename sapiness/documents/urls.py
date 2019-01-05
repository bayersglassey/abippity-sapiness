from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'^list/?$', views.DocumentListView.as_view(), name='list'),
    url(r'^detail/(?P<pk>[0-9]+)/?$', views.DocumentDetailView.as_view(), name='detail'),
    url(r'^args_help/?$', views.ArgsHelpView.as_view(), name='args_help'),
    url(r'^keywords_help/?$', views.KeywordsHelpView.as_view(), name='keywords_help'),
]
