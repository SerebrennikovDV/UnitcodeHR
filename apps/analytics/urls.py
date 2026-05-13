from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='analytics_dashboard'),
    path('api/funnel/', views.api_funnel, name='analytics_api_funnel'),
    path('export/xlsx/', views.export_xlsx, name='analytics_export'),
]
