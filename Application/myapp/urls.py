from django.urls import path, include
from . import views
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('search-records/', views.search_records, name='search_records'),
    path('transcribe/', views.transcribe, name='transcribe'),
    path('i18n/', include('django.conf.urls.i18n')),
]
