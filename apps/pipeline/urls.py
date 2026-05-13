from django.urls import path
from . import views

urlpatterns = [
    path('', views.pipeline_board, name='pipeline_board'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('applications/<int:pk>/move/', views.application_move_stage, name='application_move'),
    path('applications/<int:pk>/restore/', views.application_restore, name='application_restore'),
    path('interviews/new/<int:app_pk>/', views.interview_schedule, name='interview_schedule'),
]
