from django.urls import path
from . import views

urlpatterns = [
    path('strings', views.create_analyze_string, name='create-analyze-string'),
    path('strings/<str:string_value>', views.string_detail, name='string-detail'),
    path('strings/filter-by-natural-language', views.filter_by_natural_language, name='filter-natural-language'),
]