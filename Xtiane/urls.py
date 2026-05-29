from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView  
from django.contrib.auth import logout  # <-- Logout
from django.contrib.auth import views as auth_views  # <--- IMPORTACIÓN OBLIGATORIA
from django.conf import settings  # ✅ Cambiado de 'from Xtiane import settings'
from django.contrib import admin
from django.urls import path, include
from usuarios import views
from usuarios.views import CustomLogoutView, dashboard

# from Xtiane import settings


# Personalización de encabezados del sitio administrativo de la suite
admin.site.site_header = "XTIANE — Panel de Control Administrativo"
admin.site.site_title = "XTIANE Admin"
admin.site.index_title = "Módulos de Gestión Operativa (Versión 2)"



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('areas/', include('notificaciones.areas.urls')),    
    
    # path('notificaciones/areas/', include('notificaciones.areas.urls')),
    path('notificaciones/notificadores/', include('notificaciones.notificadores.urls')),     
    path('notificaciones/bitacora/', include('notificaciones.bitacora.urls')),         
    # Vista no personalizada
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
    # Cambia a vista Personalizada
     path('logout/', CustomLogoutView.as_view(), name='logout'),
     path('denegado/', TemplateView.as_view(template_name='denegado.html'), name='denegado'),     
     path('usuarios/', include('usuarios.urls')),  # ← Agregar esta línea
]


# ✅ ESTO ES LO QUE TE FALTA AGREGAR (al final del archivo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)