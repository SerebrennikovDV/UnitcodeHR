from django.urls import path
from . import views

urlpatterns = [
    path('matches/', views.match_list, name='match_list'),
    path('matches/<int:pk>/recalculate/', views.match_recalculate, name='match_recalculate'),
    path('keywords/enrich/', views.enrich_keywords, name='enrich_keywords'),
]
