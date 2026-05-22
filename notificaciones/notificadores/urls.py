# notificaciones/notificadores/urls.py
from django.urls import path
from . import views

app_name = 'notificadores'

urlpatterns = [
    path('', views.lista_notificadores, name='lista_notificadores'),
    path('crear/', views.crear_notificador, name='crear'),
    path('editar/<int:pk>/', views.editar_notificador, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_notificador, name='eliminar'),
]