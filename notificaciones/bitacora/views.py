# notificaciones/bitacora/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import date
from .models import Bitacora
from .forms import BitacoraForm
from usuarios.decorators import rol_requerido


def filtrar_por_estado(request, estado):
    print(f"=== FILTRO RECIBIDO: estado = '{estado}' ===")  # ← Línea de depuración


@rol_requerido(['developer', 'admin', 'coordinador', 'secretaria'])
def lista_bitacora(request):
    """Vista para listar todos los registros de bitácora"""
    registros = Bitacora.objects.select_related('notificador').all()
    
    # Filtrar por área si el usuario es secretaria
    if request.user.rol == 'secretaria':
        area_usuario = request.user.area
        if area_usuario:
            # Filtrar registros donde el área del notificador sea la del usuario
            registros = registros.filter(notificador__area=area_usuario)

    context = {
        'titulo': 'Bitácora de Notificaciones',
        'registros': registros,
    }
    return render(request, 'bitacora/lista_bitacora.html', context)

def crear_bitacora(request):
    """Vista para crear un nuevo registro en bitácora"""
    if request.method == 'POST':
        form = BitacoraForm(request.POST, request.FILES)
        if form.is_valid():
            registro = form.save(commit=False)
            # Asegurar que fecha_bitacora sea hoy (por si acaso)
            if not registro.fecha_bitacora:
                registro.fecha_bitacora = date.today()
            # registro.capturo = request.user.username  # ← cuando tengas autenticación
            registro.save()
            messages.success(request, f'✅ Registro {registro.oficio_memo} creado exitosamente!')
            return redirect('bitacora:lista_bitacora')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = BitacoraForm()
    
    context = {
        'titulo': 'Nuevo Registro en Bitácora',
        'form': form,
        'boton_texto': 'Guardar Registro',
    }
    return render(request, 'bitacora/form_bitacora.html', context)

def editar_bitacora(request, pk):
    """Vista para editar un registro existente"""
    registro = get_object_or_404(Bitacora, pk=pk)
    
    if request.method == 'POST':
        form = BitacoraForm(request.POST, request.FILES, instance=registro)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Registro {registro.oficio_memo} actualizado exitosamente!')
            return redirect('bitacora:lista_bitacora')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = BitacoraForm(instance=registro)
    
    context = {
        'titulo': 'Editar Registro',
        'form': form,
        'registro': registro,
        'boton_texto': 'Actualizar Registro',
    }
    return render(request, 'bitacora/form_bitacora.html', context)

def eliminar_bitacora(request, pk):
    """Vista para eliminar un registro"""
    registro = get_object_or_404(Bitacora, pk=pk)
    
    if request.method == 'POST':
        oficio = registro.oficio_memo
        registro.delete()
        messages.success(request, f'🗑️ Registro {oficio} eliminado exitosamente!')
        return redirect('bitacora:lista_bitacora')
    
    context = {
        'registro': registro,
    }
    return render(request, 'bitacora/confirmar_eliminar.html', context)

def ver_bitacora(request, pk):
    """Vista para ver detalle de un registro"""
    registro = get_object_or_404(Bitacora, pk=pk)
    
    context = {
        'titulo': 'Detalle de Registro',
        'registro': registro,
        'estado_visual': registro.get_estado_visual(),
        'texto_estado': registro.get_texto_estado(),
        'color_estado': registro.get_color_estado(),
        'dias_restantes': registro.dias_restantes,
    }
    return render(request, 'bitacora/detalle_bitacora.html', context)

def cambiar_situacion(request, pk, nueva_situacion):
    """Vista para cambiar la situación de un registro"""
    registro = get_object_or_404(Bitacora, pk=pk)
    
    # Validar que la nueva situación sea válida
    situaciones_validas = [choice[0] for choice in Bitacora.SITUACIONES]
    if nueva_situacion not in situaciones_validas:
        messages.error(request, 'Situación no válida')
        return redirect('bitacora:lista_bitacora')
    
    # Si se marca como entregada, actualizar fecha_acuse automáticamente
    if nueva_situacion == Bitacora.SITUACION_ENTREGADA and not registro.fecha_acuse:
        registro.fecha_acuse = date.today()
    
    registro.situacion = nueva_situacion
    registro.save()
    
    messages.success(request, f'✅ Registro {registro.oficio_memo} actualizado a: {nueva_situacion}')
    return redirect('bitacora:lista_bitacora')

def filtrar_por_estado(request, estado):
    """Vista para filtrar registros por estado visual"""
    registros = Bitacora.objects.select_related('notificador').all()
    
    if estado == 'entregadas':
        registros = registros.filter(situacion=Bitacora.SITUACION_ENTREGADA)
        titulo_filtro = 'Entregadas'
    elif estado == 'expiradas':
        registros = [r for r in registros if r.get_estado_visual() == Bitacora.ESTADO_VISUAL_EXPIRADA]
        titulo_filtro = 'Expiradas'
    elif estado == 'expirando':
        registros = [r for r in registros if r.get_estado_visual() == Bitacora.ESTADO_VISUAL_EXPIRANDO]
        titulo_filtro = 'Expirando'
    elif estado == 'en_ruta':
        registros = registros.filter(situacion=Bitacora.SITUACION_EN_RUTA)
        titulo_filtro = 'En Ruta'
    elif estado == 'asignada' or estado == 'asignadas':
        registros = registros.filter(situacion=Bitacora.SITUACION_ASIGNADA)
        titulo_filtro = 'Asignadas'
    else:
        return redirect('bitacora:lista_bitacora')
    
    context = {
        'titulo': f'Bitácora - {titulo_filtro}',
        'registros': registros,
        'filtro_activo': estado,
    }
    return render(request, 'bitacora/lista_bitacora.html', context)

def buscar_bitacora(request):
    """Vista para buscar registros"""
    query = request.GET.get('q', '')
    registros = Bitacora.objects.select_related('notificador').all()
    
    if query:
        registros = registros.filter(
            Q(oficio_memo__icontains=query) |
            Q(destinatario__icontains=query) |
            Q(expediente_asunto__icontains=query) |
            Q(notificador__apellido1__icontains=query) |
            Q(notificador__nombres__icontains=query)
        )
        
        context = {
            'titulo': f'Resultados de búsqueda: "{query}"',
            'registros': registros,
            'query': query,
        }
    else:
        return redirect('bitacora:lista_bitacora')
    
    return render(request, 'bitacora/lista_bitacora.html', context)