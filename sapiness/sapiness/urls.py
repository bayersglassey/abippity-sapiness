"""sapiness URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView, CreateView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

class HomeView(TemplateView):
    template_name = 'index.html'

class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/register.html'
    success_url = '/'
    def form_valid(self, form):
        _return = super().form_valid(form)
        login(self.request, self.object)
        return _return


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^register/?$', RegisterView.as_view(), name='register'),
    url(r'^documents/', include('documents.urls', namespace='documents')),
    url(r'^admin/', admin.site.urls),
]



if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        #path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
