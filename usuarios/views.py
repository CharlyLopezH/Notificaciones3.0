# usuarios/views.py
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .decorators import rol_requerido
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib import messages

from notificaciones.areas.models import Area
from .models import UsuarioPerfil

class CustomLogoutView(LogoutView):
    """Vista personalizada de logout con mensaje de despedida"""
    
    def dispatch(self, request, *args, **kwargs):
        # Agregar mensaje antes de cerrar sesión
        messages.success(request, '👋 ¡Gracias por usar nuestras aplicaciones! Vuelva pronto.')
        
        # Llamar al logout original
        response = super().dispatch(request, *args, **kwargs)
        
        return response

def es_rol_privilegiado(user):
    """Roles que tienen acceso a gestión de usuarios"""
    return user.rol in ['coordinador', 'developer']  # Roles Privilegiados

# ============================================
# DASHBOARD - Acceso para todos los roles
# ============================================
@login_required
def dashboard(request):
    """Vista principal después del login"""
    context = {
        'usuario': request.user,
        'rol': request.user.rol,
        'area': request.user.area,
    }
    return render(request, 'dashboard.html', context)




# ============================================
# LISTA DE USUARIOS - Solo coordinador y developer
# ============================================
@login_required
@rol_requerido(['coordinador', 'developer'])  # Solo estos roles
def lista_usuarios(request):
    """Listado de usuarios del sistema"""
    usuarios = UsuarioPerfil.objects.select_related('area').all()
    
    context = {
        'titulo': 'Administración de Usuarios',
        'usuarios': usuarios,
    }
    return render(request, 'usuarios/lista_usuarios.html', context)


# ============================================
# CREAR USUARIO - Solo coordinador y developer
# ============================================
@login_required
@rol_requerido(['coordinador', 'developer'])
def crear_usuario(request):
    """Crear nuevo usuario"""
    areas = Area.objects.all()
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        rol = request.POST.get('rol')
        area_id = request.POST.get('area')
        email = request.POST.get('email', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Validar que el usuario no exista
        if UsuarioPerfil.objects.filter(username=username).exists():
            messages.error(request, f'El usuario {username} ya existe')
            return redirect('usuarios:crear')
        
        # Crear usuario
        usuario = UsuarioPerfil(
            username=username,
            password=make_password(password),
            rol=rol,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=(rol in ['coordinador', 'developer']),  # Simplificado
            is_active=True,
        )
        
        if area_id:
            usuario.area_id = area_id
        
        usuario.save()
        
        messages.success(request, f'✅ Usuario {username} creado exitosamente')
        return redirect('usuarios:lista_usuarios')
    
    context = {
        'titulo': 'Nuevo Usuario',
        'areas': areas,
        'roles': UsuarioPerfil.ROLES_CHOICES,
        'boton_texto': 'Crear Nuevo',
    }
    return render(request, 'usuarios/form_usuario.html', context)



# ============================================
# EDITAR USUARIO - Solo coordinador y developer
# ============================================
@login_required
@rol_requerido(['coordinador', 'developer'])
def editar_usuario(request, pk):
    """Editar usuario existente"""
    usuario = get_object_or_404(UsuarioPerfil, pk=pk)
    areas = Area.objects.all()
    
    if request.method == 'POST':
        usuario.username = request.POST.get('username')
        usuario.rol = request.POST.get('rol')
        usuario.email = request.POST.get('email', '')
        usuario.first_name = request.POST.get('first_name', '')
        usuario.last_name = request.POST.get('last_name', '')
        usuario.is_staff = (usuario.rol in ['coordinador', 'developer'])
        
        area_id = request.POST.get('area')
        if area_id:
            usuario.area_id = area_id
        else:
            usuario.area = None

        # Cambiar contraseña solo si se proporcionó una nueva
        new_password = request.POST.get('password')
        if new_password:
            usuario.password = make_password(new_password)
        
        usuario.save()
        
        messages.success(request, f'✅ Usuario {usuario.username} actualizado')
        return redirect('usuarios:lista_usuarios')
    
    context = {
        'titulo': 'Editar Usuario',
        'usuario': usuario,
        'areas': areas,
        'roles': UsuarioPerfil.ROLES_CHOICES,
        'boton_texto': 'Actualizar Usuario',
    }
    return render(request, 'usuarios/form_usuario.html', context)

# ============================================
# ELIMINAR USUARIO - Solo coordinador y developer
# ============================================
@login_required
@rol_requerido(['coordinador', 'developer'])  # Cambiado: admin NO puede eliminar
def eliminar_usuario(request, pk):
    """Eliminar usuario"""
    usuario = get_object_or_404(UsuarioPerfil, pk=pk)
    
    # No permitir eliminar el propio usuario
    if usuario.pk == request.user.pk:
        messages.error(request, 'No puedes eliminar tu propio usuario')
        return redirect('usuarios:lista_usuarios')
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'🗑️ Usuario {username} eliminado')
        return redirect('usuarios:lista_usuarios')

    context = {
        'usuario': usuario,
    }
    return render(request, 'usuarios/confirmar_eliminar.html', context)