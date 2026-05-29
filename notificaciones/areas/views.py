from pyexpat.errors import messages

from django.shortcuts import render, redirect, get_object_or_404
from .models import Area
from .forms import AreaForm
from usuarios.decorators import rol_requerido

import time




# 1. LISTAR ÁREAS
@rol_requerido(['developer', 'admin', 'secretaria','coordinador']) #Decorador que implica a los perfiles/roles señalados en el array
def lista_areas(request):
    print(f"Usuario: {request.user.username}, Rol: {request.user.rol}")  # ← Debbuging
    print("=== LLEGÓ A lista_areas ===")
    print(f"Usuario: {request.user.username}")
    print(f"Rol: {request.user.rol}")
    print(f"Área del usuario: {request.user.area}")

    from notificaciones.notificadores.models import Notificador
    from notificaciones.bitacora.models import Bitacora


@rol_requerido(['developer', 'admin', 'coordinador', 'secretaria'])
def lista_areas(request):    
    areas = Area.objects.all().order_by('id')

    # Calcular si se puede eliminar. Para cada área, determinar si hay registros relacionados
    for area in areas:
        area.puede_eliminar = not area.tiene_notificadores()  # True si NO tiene notificadores    

    # Si es secretaria, solo ve su propia área
    if request.user.rol == 'secretaria' and request.user.area:
        areas = areas.filter(id=request.user.area.id)
        print(f"🔍 Secretaria {request.user.username} - Área filtrada: {request.user.area.nombre}")
    return render(request, 'areas/lista_areas.html', {'areas': areas})

# 2. CREAR ÁREA
def crear_area(request):

    start = time.time()
    
    if request.method == 'POST':
        form = AreaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('areas:lista_areas')
    else:
        form = AreaForm()


        form = AreaForm()
    
    end = time.time()
    print(f"Tiempo de carga del formulario: {end - start} segundos")
    return render(request, 'areas/formulario_area.html', {'form': form, 'titulo': 'Registrar Nueva Área'})

# 3. EDITAR ÁREA
def editar_area(request, pk):
    area = get_object_or_404(Area.objects.all(), pk=pk)    
    if request.method == 'POST':
        form = AreaForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            return redirect('areas:lista_areas')        
    else:
        form = AreaForm(instance=area)
    return render(request, 'areas/formulario_area.html', {'form': form, 'titulo': 'Modificar Área', 'area': area})

# 4. ELIMINAR ÁREA
def eliminar_area(request, pk):
    area = get_object_or_404(Area, pk=pk)

    # Verificar dependencias antes de eliminar
    if area.tiene_dependencias():
        messages.error(request, f'No se puede eliminar el área "{area.nombre}" porque tiene registros asociados: {area.get_dependencias_texto()}')
        return redirect('areas:lista_areas')


    if request.method == 'POST':
        area.delete()
        return redirect('areas:lista_areas')
    
    context = {
        'area': area,
    }


    return render(request, 'areas/confirmar_eliminar.html', {'area': area})
