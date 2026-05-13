from django.urls import path
from . import views

urlpatterns = [
    path('', views.offer_list, name='offer_list'),
    path('<int:pk>/', views.offer_detail, name='offer_detail'),
    path('<int:pk>/generate/', views.offer_generate_docx, name='offer_generate'),
    path('<int:pk>/download/', views.offer_download, name='offer_download'),
]
