# notificaciones/bitacora/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from datetime import date
from .models import Bitacora
from .forms import BitacoraForm
from usuarios.decorators import rol_requerido

# Para los formularios de actualización
from .forms import CambioSituacionForm
from .models import SituacionActualiza

from django.http import HttpResponse


# ============================================================
# FUNCIÓN AUXILIAR - Filtra bitácoras según el rol del usuario
# ============================================================
def obtener_bitacoras_segun_rol(request):
    """Devuelve QuerySet de bitácoras filtrado según el rol del usuario"""
    from notificaciones.notificadores.models import Notificador
    
    registros = Bitacora.objects.select_related('notificador')
    
    if request.user.rol == 'notificador':
        if request.user.codigo_checador:
            empleado = Notificador.objects.filter(Codigo_Checador=str(request.user.codigo_checador)).first()
            if empleado:
                registros = registros.filter(notificador=empleado)
            else:
                registros = registros.none()
        else:
            registros = registros.none()
    
    elif request.user.rol == 'admin':
        if request.user.area:
            registros = registros.filter(notificador__area=request.user.area)
        else:
            registros = registros.none()
    
    elif request.user.rol == 'coordinador':
        if request.user.area:
            registros = registros.filter(notificador__area=request.user.area)
        else:
            registros = registros.none()
    
    elif request.user.rol == 'secretaria':
        if request.user.area:
            registros = registros.filter(notificador__area=request.user.area)
        else:
            registros = registros.none()
    
    else:
        # developer u otros roles
        registros = registros.all()
    
    return registros


# ============================================================
# VISTAS DE BITÁCORA
# ============================================================

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


@rol_requerido(['developer', 'admin', 'coordinador', 'secretaria', 'notificador'])
def lista_bitacora(request):
    """Lista de bitácoras filtrada por rol"""
    registros = obtener_bitacoras_segun_rol(request)
    
    context = {
        'titulo': 'Bitácora de Notificaciones',
        'registros': registros,
    }
    return render(request, 'bitacora/lista_bitacora.html', context)


@rol_requerido(['developer', 'admin', 'coordinador'])
def crear_bitacora(request):
    """Vista para crear un nuevo registro en bitácora"""
    if request.method == 'POST':
        form = BitacoraForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            registro = form.save(commit=False)
            if not registro.fecha_bitacora:
                registro.fecha_bitacora = date.today()
            registro.fecha_bitacora = date.today()  # ← Asegurar la fecha de la bitácora (registro)
            registro.capturo = request.user.username  # ← Asignar el usuario que captura
            registro.save()
            messages.success(request, f'✅ ¡Registro {registro.oficio_memo} creado exitosamente!')
            return redirect('bitacora:lista_bitacora')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = BitacoraForm(user=request.user)
        # Inicializar el formulario con fecha de hoy
        initial_data = {'fecha_bitacora': date.today()}  # ← AGREGA ESTO
        form = BitacoraForm(user=request.user, initial=initial_data)  # ← MODIFICA ESTO    


    context = {
        'titulo': 'Asignación de Notificación',
        'form': form,
        'boton_texto': 'Guardar',
        'fecha_hoy': date.today().strftime('%Y-%m-%d'),  # ← Enviar fecha al template
    }
    return render(request, 'bitacora/form_bitacora.html', context)

#------------------------------------------------------------------
# Para formato de Editar Bitácora
#------------------------------------------------------------------
@rol_requerido(['developer', 'admin', 'coordinador'])
def editar_bitacora(request, pk):
    """Vista para editar un registro existente"""
    registro = get_object_or_404(Bitacora, pk=pk)
    
    if request.method == 'POST':
        form = BitacoraForm(request.POST, request.FILES, instance=registro, user=request.user)
        if form.is_valid():
            registro = form.save(commit=False)
            form.save()
            messages.success(request, f'✅ Registro {registro.oficio_memo} actualizado exitosamente.')
            return redirect('bitacora:lista_bitacora')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = BitacoraForm(instance=registro, user=request.user)
    
    context = {
        'titulo': 'Editar Registro',
        'form': form,
        'registro': registro,
        'boton_texto': 'Actualizar Registro',
    }
    return render(request, 'bitacora/form_bitacora.html', context)


@rol_requerido(['developer', 'admin'])
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


@rol_requerido(['developer', 'admin', 'coordinador', 'notificador'])
def cambiar_situacion(request, pk, nueva_situacion):
    """Vista para cambiar la situación de un registro"""
    registro = get_object_or_404(Bitacora, pk=pk)
    
    # Validar que el notificador solo cambie sus propias notificaciones
    if request.user.rol == 'notificador' and request.user.codigo_checador:
        from notificaciones.notificadores.models import Notificador
        empleado = Notificador.objects.filter(Codigo_Checador=request.user.codigo_checador).first()
        if empleado and registro.notificador != empleado:
            messages.error(request, 'No tienes permiso para modificar esta notificación')
            return redirect('bitacora:lista_bitacora')
    
    situaciones_validas = [choice[0] for choice in Bitacora.SITUACIONES]
    if nueva_situacion not in situaciones_validas:
        messages.error(request, 'Situación no válida')
        return redirect('bitacora:lista_bitacora')
    
    if nueva_situacion == Bitacora.SITUACION_ENTREGADA and not registro.fecha_acuse:
        registro.fecha_acuse = date.today()
    
    registro.situacion = nueva_situacion
    registro.save()
    
    messages.success(request, f'✅ Registro {registro.oficio_memo} actualizado a: {nueva_situacion}')
    return redirect('bitacora:lista_bitacora')


@rol_requerido(['developer', 'admin', 'coordinador', 'secretaria', 'notificador'])
def filtrar_por_estado(request, estado):
    """Vista para filtrar registros por estado visual"""
    # Obtener registros base filtrados por rol
    registros = obtener_bitacoras_segun_rol(request)
    
    if estado == 'entregadas':
        registros = registros.filter(situacion=Bitacora.SITUACION_ENTREGADA)
        titulo_filtro = 'Entregadas'
    elif estado == 'expiradas':
        # Este filtro necesita lógica especial porque es por estado visual
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


@rol_requerido(['developer', 'admin', 'coordinador', 'secretaria', 'notificador'])
def buscar_bitacora(request):
    """Vista para buscar registros"""
    query = request.GET.get('q', '')
    
    # Obtener registros base filtrados por rol
    registros = obtener_bitacoras_segun_rol(request)
    
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
        return render(request, 'bitacora/lista_bitacora.html', context)
    
    # Si no hay query, mostrar todos los registros filtrados
    context = {
        'titulo': 'Bitácora de Notificaciones',
        'registros': registros,
    }
    return render(request, 'bitacora/lista_bitacora.html', context)


@rol_requerido(['developer', 'admin', 'coordinador', 'notificador'])
def cambiar_situacion_form(request, pk):
    """Vista con formulario para cambiar la situación"""
    registro = get_object_or_404(Bitacora, pk=pk)

    # Validar que el notificador solo cambie sus propias notificaciones
    if request.user.rol == 'notificador' and request.user.codigo_checador:
        from notificaciones.notificadores.models import Notificador
        empleado = Notificador.objects.filter(Codigo_Checador=str(request.user.codigo_checador)).first()
        if empleado and registro.notificador != empleado:
            messages.error(request, 'No tienes permiso para modificar esta notificación')
            return redirect('bitacora:lista_bitacora')
    
    if request.method == 'POST':
        form = CambioSituacionForm(request.POST, initial={'nueva_situacion': request.POST.get('nueva_situacion')})
        if form.is_valid():
            # Guardar historial
            historial = SituacionActualiza(
                bitacora=registro,
                situacion_anterior=registro.situacion,
                situacion_nueva=request.POST.get('nueva_situacion'),
                fecha_real=form.cleaned_data.get('fecha_real'),
                notas=form.cleaned_data.get('notas'),
                notificador_codigo=str(request.user.codigo_checador) if request.user.codigo_checador else request.user.username
            )
            historial.save()
            
            # Actualizar la bitácora
            nueva_situacion = request.POST.get('nueva_situacion')
            if nueva_situacion == 'Entregada' and not registro.fecha_acuse:
                registro.fecha_acuse = form.cleaned_data.get('fecha_real') or date.today()
            
            registro.situacion = nueva_situacion
            registro.save()
            
            messages.success(request, f'✅ Situación actualizada a: {nueva_situacion}')
            return redirect('bitacora:ver', pk=registro.pk)
    else:
        form = CambioSituacionForm(initial={'nueva_situacion': registro.situacion})

    context = {
        'titulo': f'Cambiar Situación - {registro.oficio_memo}',
        'registro': registro,
        'form': form,
        'situaciones': Bitacora.SITUACIONES,
        'fecha_hoy': date.today().strftime('%Y-%m-%d'),
    }
    
    return render(request, 'bitacora/cambiar_situacion.html', context)