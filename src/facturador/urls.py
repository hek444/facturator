# myproject/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from backoffice.views import HomeRedirectView 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeRedirectView.as_view(), name='home'),
    path('backoffice/', include('backoffice.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),
]