# notificaciones/bitacora/urls.py
from django.urls import path
from . import views

app_name = 'bitacora'

urlpatterns = [
    path('', views.lista_bitacora, name='lista_bitacora'),
    path('crear/', views.crear_bitacora, name='crear'),
    path('editar/<int:pk>/', views.editar_bitacora, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_bitacora, name='eliminar'),
    path('ver/<int:pk>/', views.ver_bitacora, name='ver'),
    path('cambiar-situacion/<int:pk>/<str:nueva_situacion>/', views.cambiar_situacion, name='cambiar_situacion'),
    path('filtrar/<str:estado>/', views.filtrar_por_estado, name='filtrar'),    
    path('buscar/', views.buscar_bitacora, name='buscar'),
]