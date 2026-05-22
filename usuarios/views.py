# usuarios/views.py
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import rol_requerido

class CustomLogoutView(LogoutView):
    """Vista personalizada de logout con mensaje de despedida"""
    
    def dispatch(self, request, *args, **kwargs):
        # Agregar mensaje antes de cerrar sesión
        messages.success(request, '👋 ¡Gracias por usar nuestras aplicaciones! Vuelva pronto.')
        
        # Llamar al logout original
        response = super().dispatch(request, *args, **kwargs)
        
        return response

@login_required
@rol_requerido(['developer', 'admin', 'coordinador', 'secretaria'])
def dashboard(request):
    """Vista principal después del login"""
    context = {
        'usuario': request.user,
        'rol': request.user.rol,
        'area': request.user.area,
    }
    return render(request, 'dashboard.html', context)