from django.urls import path
from notificaciones.areas import views # type: ignore

app_name = 'areas'

urlpatterns = [
    path('', views.lista_areas, name='lista_areas'),
    path('crear/', views.crear_area, name='crear'),
    path('editar/<int:pk>/', views.editar_area, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_area, name='eliminar'),
]
