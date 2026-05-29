# usuarios/decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
import inspect

def rol_requerido(roles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificar autenticación
            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión')
                return redirect('login')
            
            # Obtener el rol del usuario
            rol_usuario = request.user.rol
            
            # Depuración
            print("=" * 60)
            print(f"📍 Vista: {view_func.__name__}")
            print(f"👤 Usuario: {request.user.username}")
            print(f"🔍 Rol: '{rol_usuario}'")
            print(f"🔑 Roles permitidos: {roles_permitidos}")
            print("=" * 60)
            
            # Developer y superusuario siempre tienen acceso total
            if rol_usuario == 'developer' or request.user.is_superuser:
                print("✅ Acceso developer/superuser")
                return view_func(request, *args, **kwargs)
            
            # Comparación normalizada (minúsculas, sin espacios)
            rol_normalizado = rol_usuario.strip().lower()
            roles_normalizados = [r.strip().lower() for r in roles_permitidos]
            
            if rol_normalizado in roles_normalizados:
                print("✅ Acceso permitido")
                return view_func(request, *args, **kwargs)
            
            # Acceso denegado
            print("❌ ACCESO DENEGADO")
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('denegado')
        
        return wrapper
    return decorator