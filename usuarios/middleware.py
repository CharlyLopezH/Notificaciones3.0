from django.shortcuts import redirect
from django.contrib import messages

class FiltroAreaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Si el usuario está autenticado y no es Developer Global, validamos su área
        if request.user.is_authenticated:
            if request.user.rol != 'developer' and not request.user.area:
                # Si un operador se quedó sin área asignada por error, lo mandamos al login
                messages.error(request, "Tu cuenta no tiene un Área asignada. Contacta al Administrador.")
                from django.contrib.auth import logout
                logout(request)
                return redirect('login')
        
        response = self.get_response(request)
        return response
