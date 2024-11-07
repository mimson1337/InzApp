from django.urls import path, include
from . import views
from django.conf.urls.i18n import i18n_patterns

# i18n_patterns pozwala na obsługę tłumaczeń w URL
urlpatterns = [
    # Wprowadź URL-e, które nie powinny być objęte tłumaczeniem
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('search-records/', views.search_records, name='search_records'),
    # path('en/search-records/', views.search_records, name='search_records'),
    # path('pl/search-records/', views.search_records, name='search_records'),
    path('transcribe/', views.transcribe, name='transcribe'),
    # path('pl/transcribe/', views.transcribe, name='transcribe'),
    path('i18n/', include('django.conf.urls.i18n')),
]
