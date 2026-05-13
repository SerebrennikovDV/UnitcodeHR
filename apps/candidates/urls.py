from django.urls import path
from . import views

urlpatterns = [
    path('', views.candidate_list, name='candidate_list'),
    path('apply/<slug:slug>/', views.apply_to_vacancy, name='apply_to_vacancy'),
    path('<int:pk>/', views.candidate_detail, name='candidate_detail'),
]
