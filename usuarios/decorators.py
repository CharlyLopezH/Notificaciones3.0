# usuarios/decorators.py
import inspect

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


# usuarios/decorators.py
def rol_requerido(roles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión')
                return redirect('login')

            # Obtener el nombre de la vista que está siendo decorada
            nombre_vista = view_func.__name__
            archivo_vista = inspect.getfile(view_func)
            
            rol_usuario = request.user.rol

            print("=" * 60)
            print(f"📍 Vista: {view_func.__name__}")
            print(f"👤 Usuario: {request.user.username}")
            print(f"🔍 Rol: '{rol_usuario}'")
            print(f"🔑 Roles permitidos: {roles_permitidos}")
            print(f"🔍 ¿Coincide exactamente? {rol_usuario in roles_permitidos}")
            print(f"🔍 ¿Coincide lower? {rol_usuario.lower() in [r.lower() for r in roles_permitidos]}")
            print("=" * 60)

                        # Developer siempre tiene acceso total
            if rol_usuario == 'developer' or request.user.is_superuser:
                print("✅ Acceso developer")
                return view_func(request, *args, **kwargs)


            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión')
                return redirect('login')
            
            # Acceso directo al campo 'rol'
            rol_usuario = request.user.rol
            
            if rol_usuario == 'developer' or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Comparación normalizada
            if rol_usuario.lower() in [r.lower() for r in roles_permitidos]:
                print("✅ Acceso permitido (normalizado)")
                return view_func(request, *args, **kwargs)
            
            # Acceso denegado
            print("❌ ACCESO DENEGADO")
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('denegado')
        return wrapper

        
    return decorator