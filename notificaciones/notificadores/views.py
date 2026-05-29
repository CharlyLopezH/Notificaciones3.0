# notificaciones/notificadores/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import Notificador
from .forms import NotificadorForm
from usuarios.decorators import rol_requerido


def lista_notificadores(request):
    """Vista para listar todos los notificadores"""
    notificadores = Notificador.objects.select_related('area').all()

    if request.user.rol == 'coordinador' and request.user.area:
        notificadores = notificadores.filter(area=request.user.area) 

    # Determinar si se puede eliminar cada notificador en la lista (controlar aspecto del botón eliminar)
    for notificador in notificadores:
        notificador.puede_eliminar = not notificador.tiene_bitacoras()
    
    context = {
        'titulo': 'Listado de Notificadores',
        'notificadores': notificadores,
    }
    return render(request, 'notificadores/lista_notificadores.html', context)

def crear_notificador(request):
    """Vista para crear un nuevo notificador"""
    if request.method == 'POST':
        form = NotificadorForm(request.POST, request.FILES)
        if form.is_valid():
            notificador = form.save()
            messages.success(request, f'¡Notificador {notificador.nombre_completo()} agregado exitosamente!')
            return redirect('notificadores:lista_notificadores')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = NotificadorForm()
    
    context = {
        'titulo': 'Nuevo Notificador',
        'form': form,
        'boton_texto': 'Guardar Notificador',
    }
    return render(request, 'notificadores/form_notificador.html', context)

def editar_notificador(request, pk):
    """Vista para editar un notificador existente"""
    notificador = get_object_or_404(Notificador, pk=pk)
    
    if request.method == 'POST':
        form = NotificadorForm(request.POST, request.FILES, instance=notificador)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡Notificador {notificador.nombre_completo()} actualizado exitosamente!')
            return redirect('notificadores:lista_notificadores')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = NotificadorForm(instance=notificador)
    
    context = {
        'titulo': 'Editar Notificador',
        'form': form,
        'notificador': notificador,
        'boton_texto': 'Actualizar Notificador',
    }
    return render(request, 'notificadores/form_notificador.html', context)

def eliminar_notificador(request, pk):
    """Vista para eliminar un notificador"""
    notificador = get_object_or_404(Notificador, pk=pk)

        # Validar que no tenga bitácoras
    if notificador.tiene_bitacoras():
        messages.error(request, f'No se puede eliminar "{notificador.nombre_completo}" porque tiene bitácoras asociadas')
        return redirect('notificadores:lista_notificadores')
    
    if request.method == 'POST':
        nombre = notificador.nombre_completo
        notificador.delete()
        messages.success(request, f'¡Notificador {nombre} eliminado exitosamente!')
        return redirect('notificadores:lista_notificadores')
    
    context = {
        'notificador': notificador,
    }
    return render(request, 'notificadores/confirmar_eliminar.html', context)