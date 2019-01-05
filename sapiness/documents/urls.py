from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^list/?$', views.DocumentListView.as_view(), name='list'),
    url(r'^detail/(?P<pk>[0-9]+)/?$', views.DocumentDetailView.as_view(), name='detail'),
]
