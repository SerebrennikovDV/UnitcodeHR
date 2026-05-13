from django.urls import path
from . import views

urlpatterns = [
    path('', views.vacancy_list, name='vacancy_list'),
    path('public/<slug:slug>/', views.vacancy_public_detail, name='vacancy_public'),
    path('<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
    path('requests/', views.hiring_request_list, name='hiring_request_list'),
    path('requests/new/', views.hiring_request_create, name='hiring_request_create'),
    path('requests/<int:pk>/', views.hiring_request_detail, name='hiring_request_detail'),
]
