from django.urls import path
from . import views

urlpatterns = [
    path('strings/filter-by-natural-language', views.natural_language_search, name='filter-natural-language'),
    path('strings', views.create_analyze_string, name='create-analyze-string'),
    path('strings/<str:string_value>', views.string_detail, name='string-detail'),
    path('clear-db', views.clear_database, name='clear-db'),
    path('test-natural', views.test_natural, name='test-natural'),
]