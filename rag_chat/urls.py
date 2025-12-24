from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/upload/', views.upload_document, name='upload_document'),
    path('api/chat/', views.chat, name='chat'),
]
