from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg, F
from django.db.models.functions import Extract
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import json
from .models import Cliente, Cancha, TipoCancha, Reserva, Servicio, Torneo, Pago, Equipo, Partido


#  VISTA PRINCIPAL 

def home(request):
    hoy = timezone.now().date()
    torneos_vigentes = Torneo.objects.filter(fecha_fin__gte=hoy).count()
    
    context = {
        'total_clientes': Cliente.objects.count(),
        'total_canchas': Cancha.objects.count(),
        'reservas_activas': Reserva.objects.filter(estado='PAGADA').count(),
        'reservas_pendientes': Reserva.objects.filter(estado='PENDIENTE').count(),
        'torneos_vigentes': torneos_vigentes,
    }
    return render(request, 'reservas/home.html', context)

def cliente_lista(request):
    clientes_list = Cliente.objects.all()
    
    # Búsqueda del lado del servidor
    search_query = request.GET.get('search', '').strip()
    if search_query:
        clientes_list = clientes_list.filter(
            Q(nombre__icontains=search_query) |
            Q(apellido__icontains=search_query) |
            Q(dni__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(telefono__icontains=search_query)
        )
    
    clientes_list = clientes_list.order_by('apellido', 'nombre')
    
    # Paginación: 10 clientes por página
    paginator = Paginator(clientes_list, 10)
    page = request.GET.get('page', 1)
    
    try:
        clientes = paginator.page(page)
    except PageNotAnInteger:
        clientes = paginator.page(1)
    except EmptyPage:
        clientes = paginator.page(paginator.num_pages)
    
    context = {
        'clientes': clientes,
        'search_query': search_query,
    }
    return render(request, 'reservas/clientes/lista.html', context)

def cliente_crear(request):
    if request.method == 'POST':
        try:
            # Verificar si el DNI ya existe
            dni = request.POST['dni'].strip()
            if Cliente.objects.filter(dni=dni).exists():
                messages.error(request, f'Ya existe un cliente con el DNI {dni}. Por favor, verifica los datos.')
                return render(request, 'reservas/clientes/form.html')
            
            # Verificar si el email ya existe
            email = request.POST['email'].strip()
            if Cliente.objects.filter(email=email).exists():
                messages.error(request, f'Ya existe un cliente con el email {email}. Por favor, usa otro email.')
                return render(request, 'reservas/clientes/form.html')
            
            # Crear cliente sin guardar aún
            cliente = Cliente(
                nombre=request.POST['nombre'],
                apellido=request.POST['apellido'],
                dni=dni,
                email=email,
                telefono=request.POST['telefono']
            )
            
            # Validar antes de guardar
            cliente.full_clean()
            cliente.save()
            
            messages.success(request, f'Cliente {cliente.nombre} {cliente.apellido} creado exitosamente.')
            return redirect('cliente_lista')
        except ValidationError as e:
            # Manejar errores de validación específicos
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f'{field.capitalize()}: {error}')
            else:
                messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al crear cliente: {str(e)}')
    
    return render(request, 'reservas/clientes/form.html')

def cliente_editar(request, pk):
    """Editar un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        try:
            # Verificar si el DNI ya existe en otro cliente
            dni = request.POST['dni'].strip()
            if Cliente.objects.filter(dni=dni).exclude(pk=pk).exists():
                messages.error(request, f'Ya existe otro cliente con el DNI {dni}. Por favor, verifica los datos.')
                return render(request, 'reservas/clientes/form.html', {'cliente': cliente})
            
            # Verificar si el email ya existe en otro cliente
            email = request.POST['email'].strip()
            if Cliente.objects.filter(email=email).exclude(pk=pk).exists():
                messages.error(request, f'Ya existe otro cliente con el email {email}. Por favor, usa otro email.')
                return render(request, 'reservas/clientes/form.html', {'cliente': cliente})
            
            # Actualizar campos
            cliente.nombre = request.POST['nombre']
            cliente.apellido = request.POST['apellido']
            cliente.dni = dni
            cliente.email = email
            cliente.telefono = request.POST['telefono']
            
            # Validar antes de guardar
            cliente.full_clean()
            cliente.save()
            
            messages.success(request, f'Cliente {cliente.nombre} {cliente.apellido} actualizado exitosamente.')
            return redirect('cliente_detalle', pk=pk)
        except ValidationError as e:
            # Manejar errores de validación específicos
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f'{field.capitalize()}: {error}')
            else:
                messages.error(request, str(e))
            return render(request, 'reservas/clientes/form.html', {'cliente': cliente})
        except Exception as e:
            messages.error(request, f'Error al actualizar cliente: {str(e)}')
            return render(request, 'reservas/clientes/form.html', {'cliente': cliente})
            return redirect('cliente_lista')
        except Exception as e:
            messages.error(request, f'Error al actualizar cliente: {str(e)}')
    
    return render(request, 'reservas/clientes/form.html', {'cliente': cliente})

def cliente_eliminar(request, pk):
    """Eliminar un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        nombre_completo = f'{cliente.nombre} {cliente.apellido}'
        cliente.delete()
        messages.success(request, f'Cliente {nombre_completo} eliminado exitosamente.')
        return redirect('cliente_lista')
    
    return render(request, 'reservas/clientes/confirmar_eliminar.html', {'cliente': cliente})

def cliente_detalle(request, pk):
    """Ver detalle de un cliente y sus reservas"""
    cliente = get_object_or_404(Cliente, pk=pk)
    reservas = cliente.reservas.all().order_by('-fecha_hora_inicio')
    return render(request, 'reservas/clientes/detalle.html', {
        'cliente': cliente,
        'reservas': reservas
    })

def cancha_lista(request):
    """Listar todas las canchas con paginación y búsqueda"""
    canchas_list = Cancha.objects.all().select_related('tipo_cancha')
    tipos_cancha = TipoCancha.objects.all()
    
    # Búsqueda del lado del servidor
    search_query = request.GET.get('search', '').strip()
    if search_query:
        canchas_list = canchas_list.filter(
            Q(nombre__icontains=search_query) |
            Q(tipo_cancha__nombre__icontains=search_query)
        )
    
    canchas_list = canchas_list.order_by('nombre')
    
    # Paginación: 10 canchas por página
    paginator = Paginator(canchas_list, 10)
    page = request.GET.get('page', 1)
    
    try:
        canchas = paginator.page(page)
    except PageNotAnInteger:
        canchas = paginator.page(1)
    except EmptyPage:
        canchas = paginator.page(paginator.num_pages)
    
    context = {
        'canchas': canchas,
        'tipos_cancha': tipos_cancha,
        'search_query': search_query,
    }
    return render(request, 'reservas/canchas/lista.html', context)

def cancha_crear(request):
    """Crear una nueva cancha"""
    if request.method == 'POST':
        try:
            tipo_cancha = get_object_or_404(TipoCancha, pk=request.POST['tipo_cancha'])
            cancha = Cancha.objects.create(
                nombre=request.POST['nombre'],
                tipo_cancha=tipo_cancha,
                precio_por_hora=request.POST['precio_por_hora'],
                activa=request.POST.get('activa') == 'on'
            )
            messages.success(request, f'Cancha {cancha.nombre} creada exitosamente.')
            return redirect('cancha_lista')
        except Exception as e:
            messages.error(request, f'Error al crear cancha: {str(e)}')
    
    tipos_cancha = TipoCancha.objects.all()
    return render(request, 'reservas/canchas/form.html', {'tipos_cancha': tipos_cancha})

def cancha_editar(request, pk):
    """Editar una cancha existente"""
    cancha = get_object_or_404(Cancha, pk=pk)
    
    if request.method == 'POST':
        try:
            tipo_cancha = get_object_or_404(TipoCancha, pk=request.POST['tipo_cancha'])
            cancha.nombre = request.POST['nombre']
            cancha.tipo_cancha = tipo_cancha
            cancha.precio_por_hora = request.POST['precio_por_hora']
            cancha.activa = request.POST.get('activa') == 'on'
            cancha.save()
            messages.success(request, f'Cancha {cancha.nombre} actualizada exitosamente.')
            return redirect('cancha_lista')
        except Exception as e:
            messages.error(request, f'Error al actualizar cancha: {str(e)}')
    
    tipos_cancha = TipoCancha.objects.all()
    return render(request, 'reservas/canchas/form.html', {
        'cancha': cancha,
        'tipos_cancha': tipos_cancha
    })

def cancha_eliminar(request, pk):
    """Eliminar una cancha"""
    cancha = get_object_or_404(Cancha, pk=pk)
    
    if request.method == 'POST':
        nombre = cancha.nombre
        cancha.delete()
        messages.success(request, f'Cancha {nombre} eliminada exitosamente.')
        return redirect('cancha_lista')
    
    return render(request, 'reservas/canchas/confirmar_eliminar.html', {'cancha': cancha})

def cancha_detalle(request, pk):
    """Ver detalle de una cancha y sus reservas"""
    cancha = get_object_or_404(Cancha, pk=pk)
    reservas = cancha.reservas.all().order_by('-fecha_hora_inicio')[:10]
    return render(request, 'reservas/canchas/detalle.html', {
        'cancha': cancha,
        'reservas': reservas
    })

def reserva_lista(request):
    """Listar todas las reservas con filtros opcionales y paginación"""
    reservas_list = Reserva.objects.all().select_related('cliente', 'cancha', 'torneo').order_by('-id')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        reservas_list = reservas_list.filter(estado=estado)
    
    cliente_id = request.GET.get('cliente')
    if cliente_id:
        reservas_list = reservas_list.filter(cliente_id=cliente_id)
    
    cancha_id = request.GET.get('cancha')
    if cancha_id:
        reservas_list = reservas_list.filter(cancha_id=cancha_id)
    
    # Paginación: 15 reservas por página
    paginator = Paginator(reservas_list, 15)
    page = request.GET.get('page', 1)
    
    try:
        reservas = paginator.page(page)
    except PageNotAnInteger:
        reservas = paginator.page(1)
    except EmptyPage:
        reservas = paginator.page(paginator.num_pages)
    
    clientes = Cliente.objects.all().order_by('id')
    canchas = Cancha.objects.all().order_by('id')
    
    response = render(request, 'reservas/reservas/lista.html', {
        'reservas': reservas,
        'clientes': clientes,
        'canchas': canchas,
        'estados': Reserva.ESTADO_CHOICES
    })
    # Agregar headers para evitar caché
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def reserva_crear(request):
    """Crear una nueva reserva con validación de disponibilidad"""
    if request.method == 'POST':
        # Función auxiliar para preparar el contexto del formulario
        def preparar_contexto_formulario(mantener_datos=False, limpiar_fechas=False):
            clientes = Cliente.objects.all().order_by('apellido', 'nombre')
            canchas = Cancha.objects.all().order_by('nombre')
            servicios = Servicio.objects.all()
            torneos = Torneo.objects.all()
            reservas_activas = Reserva.objects.filter(estado__in=['PENDIENTE', 'PAGADA']).values('id', 'cancha_id', 'fecha_hora_inicio', 'fecha_hora_fin', 'estado')
            import json
            reservas_json = json.dumps([{
                'id': r['id'],
                'cancha_id': r['cancha_id'],
                'fecha_hora_inicio': r['fecha_hora_inicio'].isoformat(),
                'fecha_hora_fin': r['fecha_hora_fin'].isoformat(),
                'estado': r['estado']
            } for r in reservas_activas])
            
            contexto = {
                'clientes': clientes,
                'canchas': canchas,
                'servicios': servicios,
                'torneos': torneos,
                'estados': Reserva.ESTADO_CHOICES,
                'reservas_json': reservas_json
            }
            
            # Si mantener_datos es True, preservar los datos del POST
            if mantener_datos:
                contexto['datos_form'] = {
                    'cliente_id': request.POST.get('cliente', ''),
                    'cancha_id': request.POST.get('cancha', ''),
                    # Si limpiar_fechas es True, no pasar las fechas
                    'fecha_hora_inicio': '' if limpiar_fechas else request.POST.get('fecha_hora_inicio', ''),
                    'fecha_hora_fin': '' if limpiar_fechas else request.POST.get('fecha_hora_fin', ''),
                    'servicios_ids': request.POST.getlist('servicios'),
                    'torneo_id': request.POST.get('torneo', ''),
                }
            
            return contexto
        
        # Validar campos requeridos
        if 'cliente' not in request.POST or not request.POST['cliente']:
            messages.error(request, 'Debes seleccionar un cliente.')
            return render(request, 'reservas/reservas/form.html', preparar_contexto_formulario())
        
        if 'cancha' not in request.POST or not request.POST['cancha']:
            messages.error(request, 'Debes seleccionar una cancha.')
            return render(request, 'reservas/reservas/form.html', preparar_contexto_formulario())
        
        if 'fecha_hora_inicio' not in request.POST or not request.POST['fecha_hora_inicio']:
            messages.error(request, 'Debes seleccionar la fecha y hora de inicio.')
            return render(request, 'reservas/reservas/form.html', preparar_contexto_formulario(mantener_datos=True))
        
        if 'fecha_hora_fin' not in request.POST or not request.POST['fecha_hora_fin']:
            messages.error(request, 'Debes seleccionar la fecha y hora de fin.')
            return render(request, 'reservas/reservas/form.html', preparar_contexto_formulario(mantener_datos=True))
        
        try:
            # Obtener datos del formulario
            cliente = get_object_or_404(Cliente, pk=request.POST['cliente'])
            cancha = get_object_or_404(Cancha, pk=request.POST['cancha'])
            
            # Convertir fechas y hacerlas timezone-aware
            fecha_inicio_naive = datetime.fromisoformat(request.POST['fecha_hora_inicio'])
            fecha_fin_naive = datetime.fromisoformat(request.POST['fecha_hora_fin'])
            
            # Convertir a timezone-aware usando la zona horaria configurada en Django
            fecha_inicio = timezone.make_aware(fecha_inicio_naive)
            fecha_fin = timezone.make_aware(fecha_fin_naive)
            
            # Validar que la fecha de inicio no sea en el pasado
            if fecha_inicio < timezone.now():
                messages.error(request, 'No se pueden hacer reservas en el pasado. Por favor, selecciona una fecha y hora válida.')
                return render(request, 'reservas/reservas/form.html', preparar_contexto_formulario(mantener_datos=True, limpiar_fechas=True))
            
            # Validar que la fecha de fin sea posterior a la de inicio
            if fecha_fin <= fecha_inicio:
                messages.error(request, 'La fecha de fin debe ser posterior a la fecha de inicio.')
                return render(request, 'reservas/reservas/form.html', preparar_contexto_formulario(mantener_datos=True, limpiar_fechas=True))
            
            # Validar disponibilidad de la cancha
            reservas_conflicto = Reserva.objects.filter(
                cancha=cancha,
                estado__in=['PENDIENTE', 'PAGADA']
            ).filter(
                Q(fecha_hora_inicio__lt=fecha_fin) & Q(fecha_hora_fin__gt=fecha_inicio)
            )
            
            if reservas_conflicto.exists():
                messages.error(request, 'La cancha no está disponible en el horario seleccionado.')
                return render(request, 'reservas/reservas/form.html', preparar_contexto_formulario(mantener_datos=True))
            
            # Crear la reserva
            reserva = Reserva.objects.create(
                cliente=cliente,
                cancha=cancha,
                fecha_hora_inicio=fecha_inicio,
                fecha_hora_fin=fecha_fin,
                estado=request.POST.get('estado', 'PENDIENTE')
            )
            
            # Agregar servicios si se seleccionaron
            servicios_ids = request.POST.getlist('servicios')
            if servicios_ids:
                reserva.servicios.set(servicios_ids)
            
            # Agregar torneo si se seleccionó
            torneo_id = request.POST.get('torneo')
            if torneo_id:
                reserva.torneo_id = torneo_id
                reserva.save()
            
            # Calcular monto total
            horas = (fecha_fin - fecha_inicio).total_seconds() / 3600
            monto_cancha = float(cancha.precio_por_hora) * horas
            monto_servicios = sum(float(s.costo_adicional) for s in reserva.servicios.all())
            monto_total = monto_cancha + monto_servicios
            
            # Crear el pago asociado
            Pago.objects.create(
                reserva=reserva,
                monto_total=monto_total,
                estado='PENDIENTE'
            )
            
            messages.success(request, f'Reserva creada exitosamente. Monto total: ${monto_total:.2f}')
            return redirect('reserva_lista')
            
        except Exception as e:
            messages.error(request, f'Error al crear reserva: {str(e)}')
            return render(request, 'reservas/reservas/form.html', preparar_contexto_formulario())
    
    # Obtener todas las reservas activas para verificar disponibilidad
    import json
    from django.utils.dateformat import format as date_format
    
    reservas_activas = Reserva.objects.filter(
        estado__in=['PENDIENTE', 'PAGADA']
    ).values('id', 'cancha_id', 'fecha_hora_inicio', 'fecha_hora_fin', 'estado')
    
    # Convertir a formato JSON para JavaScript
    reservas_json = json.dumps([{
        'id': r['id'],
        'cancha_id': r['cancha_id'],
        'fecha_hora_inicio': r['fecha_hora_inicio'].isoformat(),
        'fecha_hora_fin': r['fecha_hora_fin'].isoformat(),
        'estado': r['estado']
    } for r in reservas_activas])
    
    clientes = Cliente.objects.all().order_by('apellido', 'nombre')
    canchas = Cancha.objects.all().order_by('nombre')
    servicios = Servicio.objects.all()
    torneos = Torneo.objects.all()
    
    return render(request, 'reservas/reservas/form.html', {
        'clientes': clientes,
        'canchas': canchas,
        'servicios': servicios,
        'torneos': torneos,
        'estados': Reserva.ESTADO_CHOICES,
        'reservas_json': reservas_json
    })

def reserva_editar(request, pk):
    """Editar una reserva existente"""
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        try:
            estado_anterior = reserva.estado
            estado_nuevo = request.POST['estado']
            reserva.estado = estado_nuevo
            
            # Actualizar servicios
            servicios_ids = request.POST.getlist('servicios')
            reserva.servicios.set(servicios_ids)
            
            # Actualizar torneo
            torneo_id = request.POST.get('torneo')
            if torneo_id:
                reserva.torneo_id = torneo_id
            else:
                reserva.torneo = None
            
            reserva.save()
            
            # Recalcular monto del pago y sincronizar estado
            if hasattr(reserva, 'pago'):
                horas = (reserva.fecha_hora_fin - reserva.fecha_hora_inicio).total_seconds() / 3600
                monto_cancha = float(reserva.cancha.precio_por_hora) * horas
                monto_servicios = sum(float(s.costo_adicional) for s in reserva.servicios.all())
                reserva.pago.monto_total = monto_cancha + monto_servicios
                
                # Sincronizar estado del pago con estado de la reserva
                if estado_nuevo == 'PAGADA' and estado_anterior != 'PAGADA':
                    # Se cambió a PAGADA: establecer fecha de pago
                    reserva.pago.estado = 'PAGADO'
                    if not reserva.pago.fecha_pago:
                        reserva.pago.fecha_pago = timezone.now()
                    if not reserva.pago.metodo_pago:
                        reserva.pago.metodo_pago = 'EFECTIVO'
                elif estado_nuevo == 'PENDIENTE':
                    # Se cambió a PENDIENTE: marcar pago como pendiente
                    reserva.pago.estado = 'PENDIENTE'
                    reserva.pago.fecha_pago = None
                    reserva.pago.metodo_pago = None
                elif estado_nuevo == 'CANCELADA':
                    # Se canceló: marcar pago como reembolsado si estaba pagado
                    if reserva.pago.estado == 'PAGADO':
                        reserva.pago.estado = 'REEMBOLSADO'
                    else:
                        reserva.pago.estado = 'PENDIENTE'
                
                reserva.pago.save()
            
            messages.success(request, 'Reserva actualizada exitosamente.')
            return redirect('reserva_detalle', pk=pk)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar reserva: {str(e)}')
    
    servicios = Servicio.objects.all()
    torneos = Torneo.objects.all()
    
    return render(request, 'reservas/reservas/form.html', {
        'reserva': reserva,
        'servicios': servicios,
        'torneos': torneos,
        'estados': Reserva.ESTADO_CHOICES
    })

def reserva_eliminar(request, pk):
    """Eliminar (cancelar) una reserva"""
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        reserva.estado = 'CANCELADA'
        reserva.save()
        messages.success(request, 'Reserva cancelada exitosamente.')
        return redirect('reserva_lista')
    
    return render(request, 'reservas/reservas/confirmar_eliminar.html', {'reserva': reserva})

def reserva_detalle(request, pk):
    """Ver detalle completo de una reserva"""
    reserva = get_object_or_404(Reserva, pk=pk)
    response = render(request, 'reservas/reservas/detalle.html', {'reserva': reserva})
    # Agregar headers para evitar caché
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def reserva_marcar_pagada(request, pk):
    """Marcar una reserva como pagada y establecer la fecha de pago"""
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        if reserva.estado != 'PENDIENTE':
            messages.warning(request, 'Solo se pueden marcar como pagadas las reservas pendientes.')
            return redirect('reserva_detalle', pk=pk)
        
        try:
            # Cambiar estado de la reserva
            reserva.estado = 'PAGADA'
            reserva.save()
            
            # Actualizar el pago asociado
            pago = reserva.pago
            pago.estado = 'PAGADO'
            pago.fecha_pago = timezone.now()
            pago.metodo_pago = request.POST.get('metodo_pago', 'EFECTIVO')
            pago.comprobante = request.POST.get('comprobante', '')
            pago.save()
            
            messages.success(request, f'Reserva #{reserva.id} marcada como pagada exitosamente.')
            return redirect('reserva_detalle', pk=pk)
        except Exception as e:
            messages.error(request, f'Error al marcar como pagada: {str(e)}')
            return redirect('reserva_detalle', pk=pk)
    
    # Si es GET, redirigir al detalle
    return redirect('reserva_detalle', pk=pk)


def reserva_marcar_como_pagado(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        if reserva.estado != 'PENDIENTE':
            messages.warning(request, 'Esta reserva ya no está pendiente.')
            return redirect('reserva_detalle', pk=pk)
        
        if hasattr(reserva, 'pago'):
            pago = reserva.pago
            if pago.estado != 'PAGADO':
                pago.marcar_como_pagado('EFECTIVO', 'MANUAL')
                messages.success(request, '✅ Reserva marcada como pagada exitosamente.')
            else:
                messages.info(request, 'El pago ya estaba registrado como pagado.')
        else:
            messages.error(request, 'Esta reserva no tiene un pago asociado.')
    
    return redirect('reserva_detalle', pk=pk)

def reportes(request):
    """Página de reportes según consigna: 
    1. Listado de reservas por cliente
    2. Reservas por cancha en un período
    3. Canchas más utilizadas
    4. Gráfico estadístico: utilización mensual de canchas
    """
    
    # Obtener parámetros de filtro
    hoy = timezone.now()
    mes_seleccionado = int(request.GET.get('mes', hoy.month))
    anio_seleccionado = int(request.GET.get('anio', hoy.year))
    cliente_id = request.GET.get('cliente')
    cancha_id = request.GET.get('cancha')
    
    # Crear rango de fechas para el mes seleccionado (timezone-aware)
    inicio_mes = timezone.make_aware(datetime(anio_seleccionado, mes_seleccionado, 1))
    if mes_seleccionado == 12:
        fin_mes = timezone.make_aware(datetime(anio_seleccionado + 1, 1, 1))
    else:
        fin_mes = timezone.make_aware(datetime(anio_seleccionado, mes_seleccionado + 1, 1))
    
    # Reporte 1: Listado de reservas por cliente
    clientes_con_reservas = []
    clientes = Cliente.objects.all()
    
    for cliente in clientes:
        reservas_cliente = Reserva.objects.filter(
            cliente=cliente,
            fecha_hora_inicio__gte=inicio_mes,
            fecha_hora_inicio__lt=fin_mes
        ).order_by('-fecha_hora_inicio')
        
        if reservas_cliente.exists():
            total_gasto = Decimal('0.00')
            for reserva in reservas_cliente:
                total_gasto += Decimal(str(reserva.calcular_costo_total()))
            
            clientes_con_reservas.append({
                'cliente': cliente,
                'reservas': list(reservas_cliente),
                'num_reservas': reservas_cliente.count(),
                'total_gasto': total_gasto
            })
    
    # Si hay un cliente seleccionado, filtrar
    if cliente_id:
        clientes_con_reservas = [c for c in clientes_con_reservas if str(c['cliente'].id) == cliente_id]
    
    # Ordenar por total gasto (importe) y luego por número de reservas (de mayor a menor)
    clientes_con_reservas = sorted(
        clientes_con_reservas,
        key=lambda x: (-float(x['total_gasto']), -x['num_reservas'])
    )
    
    # Reporte 2: Reservas por cancha en el período
    canchas_con_reservas = []
    canchas = Cancha.objects.all()
    
    for cancha in canchas:
        reservas_cancha = Reserva.objects.filter(
            cancha=cancha,
            fecha_hora_inicio__gte=inicio_mes,
            fecha_hora_inicio__lt=fin_mes
        ).order_by('-fecha_hora_inicio')
        
        if reservas_cancha.exists():
            total_horas = Decimal('0.00')
            total_ingresos = Decimal('0.00')
            
            for reserva in reservas_cancha:
                total_horas += Decimal(str(reserva.duracion_horas()))
                total_ingresos += Decimal(str(reserva.calcular_costo_total()))
            
            canchas_con_reservas.append({
                'cancha': cancha,
                'reservas': list(reservas_cancha),
                'num_reservas': reservas_cancha.count(),
                'total_horas': total_horas,
                'total_ingresos': total_ingresos
            })
    
    # Si hay una cancha seleccionada, filtrar
    if cancha_id:
        canchas_con_reservas = [c for c in canchas_con_reservas if str(c['cancha'].id) == cancha_id]
    
    # Ordenar por total ingresos (importe), luego por horas y reservas (de mayor a menor)
    canchas_con_reservas = sorted(
        canchas_con_reservas,
        key=lambda x: (-float(x['total_ingresos']), -float(x['total_horas']), -x['num_reservas'])
    )
    
    # ===== REPORTE 3: Canchas más utilizadas =====
    # Usar la lista ya ordenada del reporte 2
    canchas_ranking = canchas_con_reservas
    
    # ===== REPORTE 4: Gráfico estadístico - Utilización mensual de canchas =====
    # Obtener datos de los últimos 6 meses para comparativa
    meses_data = []
    for i in range(5, -1, -1):  # 6 meses hacia atrás
        mes_calc = mes_seleccionado - i
        anio_calc = anio_seleccionado
        
        while mes_calc <= 0:
            mes_calc += 12
            anio_calc -= 1
        
        inicio = timezone.make_aware(datetime(anio_calc, mes_calc, 1))
        if mes_calc == 12:
            fin = timezone.make_aware(datetime(anio_calc + 1, 1, 1))
        else:
            fin = timezone.make_aware(datetime(anio_calc, mes_calc + 1, 1))
        
        reservas_mes = Reserva.objects.filter(
            fecha_hora_inicio__gte=inicio,
            fecha_hora_inicio__lt=fin
        )
        
        total_reservas = reservas_mes.count()
        total_horas = Decimal('0.00')
        
        for reserva in reservas_mes:
            total_horas += Decimal(str(reserva.duracion_horas()))
        
        meses_nombres = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        
        meses_data.append({
            'mes': meses_nombres[mes_calc],
            'anio': anio_calc,
            'total_reservas': total_reservas,
            'total_horas': float(total_horas)
        })
    
    # Calcular porcentajes para el gráfico
    if meses_data:
        max_reservas = max(mes['total_reservas'] for mes in meses_data)
        if max_reservas > 0:
            for mes in meses_data:
                mes['porcentaje'] = (mes['total_reservas'] / max_reservas) * 100
        else:
            for mes in meses_data:
                mes['porcentaje'] = 0
    
    # Preparar contexto
    context = {
        'mes_seleccionado': mes_seleccionado,
        'anio_seleccionado': anio_seleccionado,
        'cliente_seleccionado': cliente_id,
        'cancha_seleccionada': cancha_id,
        
        # Reporte 1: Listado por cliente
        'clientes_con_reservas': clientes_con_reservas,
        
        # Reporte 2: Reservas por cancha
        'canchas_con_reservas': canchas_con_reservas,
        
        # Reporte 3: Ranking de canchas
        'canchas_ranking': canchas_ranking,
        
        # Reporte 4: Datos para gráfico
        'meses_data': meses_data,
        'meses_data_json': json.dumps(meses_data),  # Para JavaScript
        
        # Para los filtros
        'clientes': Cliente.objects.all(),
        'canchas': Cancha.objects.all(),
        'meses': [
            (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
            (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
            (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
        ],
        'anios': range(2024, hoy.year + 2),
    }
    
    return render(request, 'reservas/reportes.html', context)



def reportes_pdf(request):
    """Genera un PDF profesional con los reportes del período seleccionado"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from io import BytesIO
    import datetime
    
    # Obtener parámetros de filtro (igual que en reportes())
    mes_seleccionado = int(request.GET.get('mes', timezone.now().month))
    anio_seleccionado = int(request.GET.get('anio', timezone.now().year))
    cliente_id = request.GET.get('cliente')
    cancha_id = request.GET.get('cancha')
    
    # Crear el buffer para el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                          rightMargin=50, leftMargin=50,
                          topMargin=50, bottomMargin=50)
    
    # Contenedor para elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para subtítulos
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=6
    )
    
    # ===== ENCABEZADO =====
    elements.append(Paragraph("Sistema de Reservas de Canchas", title_style))
    elements.append(Paragraph(f"Reporte del Período: {mes_seleccionado}/{anio_seleccionado}", normal_style))
    elements.append(Paragraph(f"Fecha de generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # ===== OBTENER DATOS (reutilizar lógica de reportes()) =====
    # Filtrar reservas base
    reservas = Reserva.objects.filter(
        fecha_hora_inicio__month=mes_seleccionado,
        fecha_hora_inicio__year=anio_seleccionado
    )
    
    if cliente_id:
        reservas = reservas.filter(cliente_id=cliente_id)
    if cancha_id:
        reservas = reservas.filter(cancha_id=cancha_id)
    
    # REPORTE 1: Clientes con más reservas
    # Calcular gastos usando el modelo Pago
    clientes_data = []
    clientes_dict = {}
    
    for reserva in reservas:
        cliente_id_val = reserva.cliente.id
        if cliente_id_val not in clientes_dict:
            clientes_dict[cliente_id_val] = {
                'nombre': reserva.cliente.nombre,
                'apellido': reserva.cliente.apellido,
                'dni': reserva.cliente.dni,
                'num_reservas': 0,
                'total_gasto': 0
            }
        
        clientes_dict[cliente_id_val]['num_reservas'] += 1
        
        # Buscar el pago asociado o calcular el costo
        try:
            pago = Pago.objects.filter(reserva=reserva).first()
            if pago:
                clientes_dict[cliente_id_val]['total_gasto'] += float(pago.monto_total)
            else:
                clientes_dict[cliente_id_val]['total_gasto'] += float(reserva.calcular_costo_total())
        except Exception:
            # Si hay error con Pago, usar el cálculo directo
            clientes_dict[cliente_id_val]['total_gasto'] += float(reserva.calcular_costo_total())
    
    # Convertir a lista y ordenar
    clientes_stats = sorted(clientes_dict.values(), 
                           key=lambda x: (-x['total_gasto'], -x['num_reservas']))[:10]
    
    if clientes_stats:
        elements.append(Paragraph("1. Top 10 Clientes por Gasto Total", subtitle_style))
        
        # Crear tabla
        data = [['#', 'Cliente', 'DNI', 'Reservas', 'Gasto Total']]
        for idx, item in enumerate(clientes_stats, 1):
            data.append([
                str(idx),
                f"{item['nombre']} {item['apellido']}",
                str(item['dni']),
                str(item['num_reservas']),
                f"${item['total_gasto']:,.2f}"
            ])
        
        table = Table(data, colWidths=[0.5*inch, 2*inch, 1.2*inch, 1*inch, 1.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
    
    # REPORTE 2: Distribución por Cancha
    canchas_dict = {}
    
    for reserva in reservas:
        cancha_id_val = reserva.cancha.id
        if cancha_id_val not in canchas_dict:
            canchas_dict[cancha_id_val] = {
                'nombre': reserva.cancha.nombre,
                'tipo_deporte': reserva.cancha.tipo_cancha.nombre,
                'num_reservas': 0,
                'total_ingresos': 0,
                'total_horas': 0
            }
        
        canchas_dict[cancha_id_val]['num_reservas'] += 1
        
        # Calcular horas
        duracion = (reserva.fecha_hora_fin - reserva.fecha_hora_inicio).total_seconds() / 3600
        canchas_dict[cancha_id_val]['total_horas'] += duracion
        
        # Calcular ingresos
        try:
            pago = Pago.objects.filter(reserva=reserva).first()
            if pago:
                canchas_dict[cancha_id_val]['total_ingresos'] += float(pago.monto_total)
            else:
                canchas_dict[cancha_id_val]['total_ingresos'] += float(reserva.calcular_costo_total())
        except Exception:
            canchas_dict[cancha_id_val]['total_ingresos'] += float(reserva.calcular_costo_total())
    
    canchas_stats = sorted(canchas_dict.values(), key=lambda x: -x['total_ingresos'])
    
    if canchas_stats:
        elements.append(Paragraph("2. Distribución de Ingresos por Cancha", subtitle_style))
        
        data = [['#', 'Cancha', 'Deporte', 'Reservas', 'Horas', 'Ingresos']]
        for idx, item in enumerate(canchas_stats, 1):
            data.append([
                str(idx),
                item['nombre'],
                item['tipo_deporte'],
                str(item['num_reservas']),
                f"{item['total_horas']:.1f}h",
                f"${item['total_ingresos']:,.2f}"
            ])
        
        table = Table(data, colWidths=[0.5*inch, 1.8*inch, 1*inch, 0.8*inch, 0.8*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#84cc16')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
    
    # REPORTE 3: Ranking de Canchas por Número de Reservas
    if canchas_stats:
        elements.append(Paragraph("3. Ranking de Canchas Más Utilizadas", subtitle_style))
        
        canchas_ranking = sorted(canchas_stats, key=lambda x: -x['num_reservas'])[:10]
        
        data = [['Posición', 'Cancha', 'Tipo Deporte', 'Reservas', 'Ingresos']]
        for idx, item in enumerate(canchas_ranking, 1):
            data.append([
                f"{idx}°",
                item['nombre'],
                item['tipo_deporte'],
                str(item['num_reservas']),
                f"${item['total_ingresos']:,.2f}"
            ])
        
        table = Table(data, colWidths=[0.8*inch, 2*inch, 1.2*inch, 1*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
    
    # REPORTE 4: Estadísticas Mensuales (últimos 6 meses)
    elements.append(PageBreak())
    elements.append(Paragraph("4. Estadísticas de los Últimos 6 Meses", subtitle_style))
    
    hoy = timezone.now()
    meses_data = []
    
    for i in range(5, -1, -1):
        mes_actual = hoy - relativedelta(months=i)
        mes_num = mes_actual.month
        anio_num = mes_actual.year
        
        reservas_mes = Reserva.objects.filter(
            fecha_hora_inicio__month=mes_num,
            fecha_hora_inicio__year=anio_num
        )
        
        total_reservas = reservas_mes.count()
        total_horas = 0
        
        for reserva in reservas_mes:
            duracion = (reserva.fecha_hora_fin - reserva.fecha_hora_inicio).total_seconds() / 3600
            total_horas += duracion
        
        meses_data.append({
            'mes': mes_actual.strftime('%B'),
            'anio': anio_num,
            'reservas': total_reservas,
            'horas': total_horas
        })
    
    if meses_data:
        data = [['Mes', 'Año', 'Reservas', 'Horas Totales']]
        for item in meses_data:
            data.append([
                item['mes'],
                str(item['anio']),
                str(item['reservas']),
                f"{item['horas']:.1f}h"
            ])
        
        table = Table(data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#84cc16')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ]))
        
        elements.append(table)
    
    # RESUMEN FINAL
    elements.append(Spacer(1, 0.5*inch))
    total_reservas_periodo = reservas.count()
    
    # Calcular ingresos totales
    total_ingresos_periodo = 0
    for reserva in reservas:
        try:
            pago = Pago.objects.filter(reserva=reserva).first()
            if pago:
                total_ingresos_periodo += float(pago.monto_total)
            else:
                total_ingresos_periodo += float(reserva.calcular_costo_total())
        except Exception:
            total_ingresos_periodo += float(reserva.calcular_costo_total())
    
    resumen_text = f"""
    <b>Resumen del Período {mes_seleccionado}/{anio_seleccionado}:</b><br/>
    • Total de reservas: {total_reservas_periodo}<br/>
    • Ingresos totales: ${total_ingresos_periodo:,.2f}<br/>
    • Clientes únicos: {reservas.values('cliente').distinct().count()}<br/>
    • Canchas utilizadas: {reservas.values('cancha').distinct().count()}
    """
    
    elements.append(Paragraph(resumen_text, normal_style))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        f"Documento generado automáticamente - {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}",
        footer_style
    ))
    
    # Construir PDF
    doc.build(elements)
    
    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    filename = f"reporte_canchas_{mes_seleccionado}_{anio_seleccionado}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response



def torneo_lista(request):
    """Listar todos los torneos con paginación"""
    # Obtener torneos y ordenarlos
    torneos_list = Torneo.objects.all().order_by('-fecha_inicio')
    
    # Actualizar estados de torneos según fechas
    hoy = timezone.now().date()
    for torneo in torneos_list:
        estado_anterior = torneo.estado
        
        # Si ya pasó la fecha de inicio y está en inscripción, cambiar a EN_CURSO
        if torneo.fecha_inicio <= hoy and torneo.estado == 'INSCRIPCION':
            torneo.estado = 'EN_CURSO'
            torneo.save()
        
        # Si pasó la fecha fin, cambiar a FINALIZADO
        if hoy > torneo.fecha_fin and torneo.estado != 'FINALIZADO':
            torneo.estado = 'FINALIZADO'
            torneo.save()
    
    # Paginación: 10 torneos por página
    paginator = Paginator(torneos_list, 10)
    page = request.GET.get('page', 1)
    
    try:
        torneos_page = paginator.page(page)
    except PageNotAnInteger:
        torneos_page = paginator.page(1)
    except EmptyPage:
        torneos_page = paginator.page(paginator.num_pages)
    
    # Clasificar torneos por estado actualizado
    torneos_activos = []
    torneos_proximos = []
    torneos_finalizados = []
    
    for torneo in torneos_page:
        # Usar el estado del modelo, no calcular por fechas
        if torneo.estado == 'EN_CURSO':
            torneos_activos.append(torneo)
        elif torneo.estado == 'INSCRIPCION' and torneo.fecha_inicio > hoy:
            torneos_proximos.append(torneo)
        elif torneo.estado == 'FINALIZADO':
            torneos_finalizados.append(torneo)
        else:
            # Si está en INSCRIPCION pero ya empezó, va a activos (edge case)
            if torneo.estado == 'INSCRIPCION' and torneo.fecha_inicio <= hoy:
                torneos_activos.append(torneo)
    
    context = {
        'torneos_activos': torneos_activos,
        'torneos_proximos': torneos_proximos,
        'torneos_finalizados': torneos_finalizados,
        'total_torneos': torneos_list.count(),
        'torneos': torneos_page,  # Para la paginación
    }
    return render(request, 'reservas/torneos/lista.html', context)


def torneo_crear(request):
    """Crear un nuevo torneo"""
    if request.method == 'POST':
        try:
            # Validar que la fecha de fin sea posterior a la de inicio
            fecha_inicio = timezone.datetime.strptime(request.POST['fecha_inicio'], '%Y-%m-%d').date()
            fecha_fin = timezone.datetime.strptime(request.POST['fecha_fin'], '%Y-%m-%d').date()
            
            if fecha_fin < fecha_inicio:
                messages.error(request, 'La fecha de finalización debe ser posterior a la fecha de inicio.')
                return render(request, 'reservas/torneos/form.html')
            
            # Validar que el nombre no esté duplicado
            nombre = request.POST['nombre']
            if Torneo.objects.filter(nombre=nombre).exists():
                messages.error(request, f'Ya existe un torneo con el nombre "{nombre}". Por favor, usa otro nombre.')
                return render(request, 'reservas/torneos/form.html')
            
            torneo = Torneo.objects.create(
                nombre=nombre,
                descripcion=request.POST.get('descripcion', ''),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                premio=request.POST.get('premio', ''),
                estado=request.POST.get('estado', 'INSCRIPCION'),
                costo_inscripcion=request.POST.get('costo_inscripcion', 0) or 0,
                reglamento=request.POST.get('reglamento', ''),
            )
            messages.success(request, f'Torneo "{torneo.nombre}" creado exitosamente.')
            return redirect('torneo_detalle', pk=torneo.pk)
        except Exception as e:
            messages.error(request, f'Error al crear el torneo: {str(e)}')
            return render(request, 'reservas/torneos/form.html')
    
    return render(request, 'reservas/torneos/form.html')


def torneo_detalle(request, pk):
    """Ver detalles de un torneo"""
    torneo = get_object_or_404(Torneo, pk=pk)
    
    # Actualizar estado del torneo según las fechas
    hoy = timezone.now().date()
    estado_anterior = torneo.estado
    
    # Si ya pasó la fecha de inicio y está en inscripción, cambiar a EN_CURSO
    if torneo.fecha_inicio <= hoy and torneo.estado == 'INSCRIPCION':
        torneo.estado = 'EN_CURSO'
        torneo.save()
    
    # Si pasó la fecha fin, cambiar a FINALIZADO
    if hoy > torneo.fecha_fin and torneo.estado != 'FINALIZADO':
        torneo.estado = 'FINALIZADO'
        torneo.save()
    
    # Obtener equipos inscritos
    equipos = torneo.equipos.all().order_by('nombre')
    equipos_inscritos = equipos.count()
    
    # Calcular ingresos por inscripciones (solo costo de inscripción * equipos)
    from decimal import Decimal
    costo = torneo.costo_inscripcion if torneo.costo_inscripcion else Decimal('0.00')
    ingresos_inscripciones = costo * equipos_inscritos
    
    # Debug
    print(f"DEBUG Torneo {torneo.id}: costo={costo}, equipos={equipos_inscritos}, ingresos_inscripciones={ingresos_inscripciones}")
    
    # Calcular ingresos por reservas pagadas relacionadas al torneo
    reservas_torneo = Reserva.objects.filter(torneo=torneo, estado='PAGADA')
    ingresos_reservas = Decimal('0.00')
    for r in reservas_torneo:
        if hasattr(r, 'pago'):
            ingresos_reservas += r.pago.monto_total
    
    # Total de ingresos del torneo
    ingresos_totales = ingresos_inscripciones + ingresos_reservas
    
    # Obtener estadísticas de partidos si existen
    partidos = torneo.partidos.all().order_by('-fecha_hora')
    total_partidos = partidos.count()
    partidos_completados = partidos.filter(estado='FINALIZADO').count()
    partidos_pendientes = partidos.filter(estado='PENDIENTE').count()
    
    # Obtener últimos 5 partidos para mostrar en detalle
    ultimos_partidos = partidos[:5]
    
    # Calcular días de duración y días restantes
    dias_duracion = (torneo.fecha_fin - torneo.fecha_inicio).days + 1
    
    if torneo.fecha_inicio > hoy:
        dias_restantes = (torneo.fecha_inicio - hoy).days
    elif torneo.fecha_fin >= hoy:
        dias_restantes = (torneo.fecha_fin - hoy).days
    else:
        dias_restantes = 0
    
    context = {
        'torneo': torneo,
        'equipos': equipos,
        'equipos_inscritos': equipos_inscritos,
        'ingresos_inscripciones': ingresos_inscripciones,
        'ingresos_reservas': ingresos_reservas,
        'ingresos_totales': ingresos_totales,
        'reservas_count': reservas_torneo.count(),
        'partidos': ultimos_partidos,
        'total_partidos': total_partidos,
        'partidos_completados': partidos_completados,
        'partidos_pendientes': partidos_pendientes,
        'dias_duracion': dias_duracion,
        'dias_restantes': dias_restantes,
        'today_date': hoy,
    }
    return render(request, 'reservas/torneos/detalle.html', context)


def torneo_editar(request, pk):
    """Editar un torneo existente"""
    torneo = get_object_or_404(Torneo, pk=pk)
    
    if request.method == 'POST':
        try:
            # Validar fechas
            fecha_inicio = timezone.datetime.strptime(request.POST['fecha_inicio'], '%Y-%m-%d').date()
            fecha_fin = timezone.datetime.strptime(request.POST['fecha_fin'], '%Y-%m-%d').date()
            
            if fecha_fin < fecha_inicio:
                messages.error(request, 'La fecha de finalización debe ser posterior a la fecha de inicio.')
                return render(request, 'reservas/torneos/form.html', {'torneo': torneo})
            
            # Validar nombre único (excepto el actual)
            nombre = request.POST['nombre']
            if Torneo.objects.filter(nombre=nombre).exclude(pk=pk).exists():
                messages.error(request, f'Ya existe otro torneo con el nombre "{nombre}".')
                return render(request, 'reservas/torneos/form.html', {'torneo': torneo})
            
            torneo.nombre = nombre
            torneo.descripcion = request.POST.get('descripcion', '')
            torneo.fecha_inicio = fecha_inicio
            torneo.fecha_fin = fecha_fin
            torneo.premio = request.POST.get('premio', '')
            torneo.estado = request.POST.get('estado', 'INSCRIPCION')
            torneo.costo_inscripcion = request.POST.get('costo_inscripcion', 0) or 0
            torneo.reglamento = request.POST.get('reglamento', '')
            torneo.save()
            
            messages.success(request, f'Torneo "{torneo.nombre}" actualizado exitosamente.')
            return redirect('torneo_detalle', pk=torneo.pk)
        except Exception as e:
            messages.error(request, f'Error al actualizar el torneo: {str(e)}')
            return render(request, 'reservas/torneos/form.html', {'torneo': torneo})
    
    context = {'torneo': torneo}
    return render(request, 'reservas/torneos/form.html', context)


def torneo_eliminar(request, pk):
    """Eliminar un torneo"""
    torneo = get_object_or_404(Torneo, pk=pk)
    
    if request.method == 'POST':
        try:
            nombre = torneo.nombre
            torneo.delete()
            messages.success(request, f'Torneo "{nombre}" eliminado exitosamente.')
            return redirect('torneo_lista')
        except Exception as e:
            messages.error(request, f'Error al eliminar el torneo: {str(e)}')
            return redirect('torneo_detalle', pk=pk)
    
    context = {'torneo': torneo}
    return render(request, 'reservas/torneos/confirmar_eliminar.html', context)


def torneo_inscribir_equipo(request, pk):
    """Inscribir equipos a un torneo"""
    torneo = get_object_or_404(Torneo, pk=pk)
    
    # Actualizar estado según fechas automáticamente
    hoy = timezone.now().date()
    
    # Si ya pasó la fecha de inicio y está en inscripción, cambiar a EN_CURSO
    if torneo.fecha_inicio <= hoy and torneo.estado == 'INSCRIPCION':
        torneo.estado = 'EN_CURSO'
        torneo.save()
        messages.warning(request, f'El torneo ya comenzó (fecha de inicio: {torneo.fecha_inicio.strftime("%d/%m/%Y")}). El estado se actualizó a "En Curso".')
    
    # Si ya pasó la fecha de fin, cambiar a FINALIZADO
    if torneo.fecha_fin < hoy and torneo.estado != 'FINALIZADO':
        torneo.estado = 'FINALIZADO'
        torneo.save()
    
    # Validar que el torneo esté en inscripción (después de actualizar el estado)
    if torneo.estado != 'INSCRIPCION':
        if torneo.estado == 'EN_CURSO':
            messages.error(request, f'El torneo ya comenzó el {torneo.fecha_inicio.strftime("%d/%m/%Y")}. No se pueden inscribir más equipos.')
        elif torneo.estado == 'FINALIZADO':
            messages.error(request, 'El torneo ya finalizó. No se pueden inscribir equipos.')
        return redirect('torneo_detalle', pk=pk)
    
    if request.method == 'POST':
        equipo_id = request.POST.get('equipo_id')
        if equipo_id:
            try:
                equipo = Equipo.objects.get(id=equipo_id, activo=True)
                torneo.equipos.add(equipo)
                messages.success(request, f'Equipo "{equipo.nombre}" inscrito al torneo.')
            except Equipo.DoesNotExist:
                messages.error(request, 'El equipo seleccionado no existe o no está activo.')
        return redirect('torneo_inscribir_equipo', pk=pk)
    
    # Obtener equipos ya inscritos y disponibles
    equipos_inscritos = torneo.equipos.all().order_by('nombre')
    equipos_disponibles = Equipo.objects.filter(activo=True).exclude(id__in=torneo.equipos.all()).order_by('nombre')
    
    context = {
        'torneo': torneo,
        'equipos_inscritos': equipos_inscritos,
        'equipos_disponibles': equipos_disponibles,
    }
    return render(request, 'reservas/torneos/inscribir_equipos.html', context)


def torneo_desinscribir_equipo(request, pk, equipo_pk):
    """Desinscribir un equipo del torneo"""
    torneo = get_object_or_404(Torneo, pk=pk)
    equipo = get_object_or_404(Equipo, pk=equipo_pk)
    
    # Actualizar estado según fechas automáticamente
    hoy = timezone.now().date()
    
    # Si ya pasó la fecha de inicio y está en inscripción, cambiar a EN_CURSO
    if torneo.fecha_inicio <= hoy and torneo.estado == 'INSCRIPCION':
        torneo.estado = 'EN_CURSO'
        torneo.save()
    
    # Si ya pasó la fecha de fin, cambiar a FINALIZADO
    if torneo.fecha_fin < hoy and torneo.estado != 'FINALIZADO':
        torneo.estado = 'FINALIZADO'
        torneo.save()
    
    # Validar que el torneo esté en inscripción (después de actualizar el estado)
    if torneo.estado != 'INSCRIPCION':
        if torneo.estado == 'EN_CURSO':
            messages.error(request, f'El torneo ya comenzó el {torneo.fecha_inicio.strftime("%d/%m/%Y")}. No se pueden desinscribir equipos.')
        elif torneo.estado == 'FINALIZADO':
            messages.error(request, 'El torneo ya finalizó. No se pueden desinscribir equipos.')
        return redirect('torneo_detalle', pk=pk)
    
    torneo.equipos.remove(equipo)
    messages.success(request, f'Equipo "{equipo.nombre}" desinscrito del torneo.')
    return redirect('torneo_inscribir_equipo', pk=pk)


def torneo_generar_fixture(request, pk):
    """Generar el fixture del torneo (eliminación directa)"""
    torneo = get_object_or_404(Torneo, pk=pk)
    
    if request.method == 'POST':
        try:
            torneo.generar_fixture()
            messages.success(request, 'Fixture generado exitosamente. El torneo está en curso.')
            return redirect('torneo_fixture', pk=pk)
        except Exception as e:
            messages.error(request, f'Error al generar fixture: {str(e)}')
            return redirect('torneo_detalle', pk=pk)
    
    import math
    num_equipos = torneo.equipos.count()
    es_potencia_de_2 = num_equipos > 0 and (num_equipos & (num_equipos - 1) == 0)
    
    # Calcular estructura del torneo si es válido
    estructura = []
    error = None
    num_rondas = 0
    
    if num_equipos < 2:
        error = "Se necesitan al menos 2 equipos para generar el fixture."
    elif not es_potencia_de_2:
        error = f"La cantidad de equipos ({num_equipos}) debe ser una potencia de 2."
    else:
        num_rondas = int(math.log2(num_equipos))
        for ronda_num in range(1, num_rondas + 1):
            partidos_en_ronda = num_equipos // (2 ** ronda_num)
            
            # Nombre de la ronda
            if ronda_num == num_rondas:
                nombre = "Final"
            elif ronda_num == num_rondas - 1:
                nombre = "Semifinal"
            elif ronda_num == num_rondas - 2:
                nombre = "Cuartos de Final"
            else:
                nombre = f"Ronda {ronda_num}"
            
            estructura.append({
                'ronda': ronda_num,
                'nombre': nombre,
                'partidos': partidos_en_ronda
            })
    
    context = {
        'torneo': torneo,
        'num_equipos': num_equipos,
        'es_potencia_de_2': es_potencia_de_2,
        'error': error,
        'num_rondas': num_rondas,
        'estructura': estructura,
        'equipos': torneo.equipos.all().order_by('nombre'),
    }
    return render(request, 'reservas/torneos/generar_fixture.html', context)


def torneo_fixture(request, pk):
    """Ver el fixture completo del torneo"""
    torneo = get_object_or_404(Torneo, pk=pk)
    
    if torneo.estado == 'INSCRIPCION':
        messages.warning(request, 'El fixture aún no ha sido generado.')
        return redirect('torneo_detalle', pk=pk)
    
    # Organizar partidos por ronda
    import math
    num_equipos = torneo.equipos.count()
    total_rondas = int(math.log2(num_equipos)) if num_equipos > 0 else 0
    
    rondas = []
    for ronda_num in range(1, total_rondas + 1):
        partidos = torneo.partidos.filter(ronda=ronda_num).order_by('numero_partido')
        
        # Determinar nombre de la ronda
        if ronda_num == total_rondas:
            nombre_ronda = "Final"
        elif ronda_num == total_rondas - 1:
            nombre_ronda = "Semifinal"
        elif ronda_num == total_rondas - 2:
            nombre_ronda = "Cuartos de Final"
        else:
            nombre_ronda = f"Ronda {ronda_num}"
        
        rondas.append({
            'numero': ronda_num,
            'nombre': nombre_ronda,
            'partidos': partidos
        })
    
    context = {
        'torneo': torneo,
        'rondas': rondas,
    }
    return render(request, 'reservas/torneos/fixture.html', context)


def partido_registrar_resultado(request, pk):
    """Registrar el resultado de un partido"""
    partido = get_object_or_404(Partido, pk=pk)
    
    if partido.estado == 'FINALIZADO':
        messages.warning(request, 'Este partido ya tiene un resultado registrado.')
        return redirect('torneo_fixture', pk=partido.torneo.pk)
    
    if request.method == 'POST':
        try:
            resultado_equipo1 = int(request.POST['resultado_equipo1'])
            resultado_equipo2 = int(request.POST['resultado_equipo2'])
            
            if resultado_equipo1 < 0 or resultado_equipo2 < 0:
                messages.error(request, 'Los resultados no pueden ser negativos.')
                return render(request, 'reservas/torneos/registrar_resultado.html', {'partido': partido})
            
            if resultado_equipo1 == resultado_equipo2:
                messages.error(request, 'No puede haber empate en eliminación directa.')
                return render(request, 'reservas/torneos/registrar_resultado.html', {'partido': partido})
            
            partido.resultado_equipo1 = resultado_equipo1
            partido.resultado_equipo2 = resultado_equipo2
            
            # El clean() del modelo determinará el ganador
            partido.clean()
            partido.save()
            
            # Avanzar al ganador a la siguiente ronda
            partido.avanzar_ganador()
            
            messages.success(request, f'Resultado registrado. Ganador: {partido.ganador.nombre}')
            return redirect('torneo_fixture', pk=partido.torneo.pk)
            
        except Exception as e:
            messages.error(request, f'Error al registrar resultado: {str(e)}')
    
    # Calcular el total de rondas del torneo
    total_rondas = partido.torneo.partidos.values_list('ronda', flat=True).distinct().count()
    es_final = partido.ronda == total_rondas
    
    context = {
        'partido': partido,
        'torneo': partido.torneo,
        'es_final': es_final,
    }
    return render(request, 'reservas/torneos/registrar_resultado.html', context)


def equipo_lista(request):
    """Listar todos los equipos con paginación"""
    equipos_list = Equipo.objects.all().prefetch_related('torneos')
    
    # Paginación: 10 equipos por página
    paginator = Paginator(equipos_list, 10)
    page = request.GET.get('page', 1)
    
    try:
        equipos = paginator.page(page)
    except PageNotAnInteger:
        equipos = paginator.page(1)
    except EmptyPage:
        equipos = paginator.page(paginator.num_pages)
    
    context = {
        'equipos': equipos,
    }
    return render(request, 'reservas/equipos/lista.html', context)


def equipo_crear(request):
    """Crear un nuevo equipo"""
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre']
            
            # Validar nombre único
            if Equipo.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f'Ya existe un equipo con el nombre "{nombre}".')
                return render(request, 'reservas/equipos/form.html', {})
            
            equipo = Equipo.objects.create(
                nombre=nombre,
                logo=request.POST.get('logo', ''),
                activo=request.POST.get('activo') == 'on'
            )
            
            messages.success(request, f'Equipo "{equipo.nombre}" creado exitosamente.')
            return redirect('equipo_lista')
            
        except Exception as e:
            messages.error(request, f'Error al crear equipo: {str(e)}')
    
    return render(request, 'reservas/equipos/form.html', {})


def equipo_detalle(request, pk):
    """Ver detalles de un equipo"""
    equipo = get_object_or_404(Equipo, pk=pk)
    torneos = equipo.torneos.all()
    
    context = {
        'equipo': equipo,
        'torneos': torneos,
    }
    return render(request, 'reservas/equipos/detalle.html', context)


def equipo_editar(request, pk):
    """Editar un equipo existente"""
    equipo = get_object_or_404(Equipo, pk=pk)
    
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre']
            
            # Validar nombre único (excepto el actual)
            if Equipo.objects.filter(nombre__iexact=nombre).exclude(pk=pk).exists():
                messages.error(request, f'Ya existe otro equipo con el nombre "{nombre}".')
                return render(request, 'reservas/equipos/form.html', {
                    'equipo': equipo
                })
            
            equipo.nombre = nombre
            equipo.logo = request.POST.get('logo', '')
            equipo.activo = request.POST.get('activo') == 'on'
            equipo.save()
            
            messages.success(request, f'Equipo "{equipo.nombre}" actualizado exitosamente.')
            return redirect('equipo_detalle', pk=pk)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar equipo: {str(e)}')
    
    return render(request, 'reservas/equipos/form.html', {
        'equipo': equipo
    })


def equipo_eliminar(request, pk):
    """Eliminar un equipo"""
    equipo = get_object_or_404(Equipo, pk=pk)
    
    # Verificar si el equipo está en algún torneo
    torneos_activos = equipo.torneos.filter(activo=True)
    if torneos_activos.exists():
        messages.error(request, f'No se puede eliminar el equipo porque está inscrito en {torneos_activos.count()} torneo(s) activo(s).')
        return redirect('equipo_detalle', pk=pk)
    
    if request.method == 'POST':
        nombre = equipo.nombre
        equipo.delete()
        messages.success(request, f'Equipo "{nombre}" eliminado exitosamente.')
        return redirect('equipo_lista')
    
    context = {
        'equipo': equipo
    }
    return render(request, 'reservas/equipos/confirmar_eliminar.html', context)

def reserva_crear_pago_mercadopago(request, pk):
    from django.conf import settings
    import mercadopago
    
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if not hasattr(reserva, 'pago'):
        try:
            costo_total = reserva.calcular_costo_total()
            Pago.objects.create(
                reserva=reserva,
                monto_total=costo_total,
                estado='PENDIENTE'
            )
        except Exception as e:
            messages.error(request, f'Error al crear el pago: {str(e)}')
            return redirect('reserva_detalle', pk=pk)
    
    pago = reserva.pago
    
    if pago.estado != 'PENDIENTE':
        messages.warning(request, 'Esta reserva ya fue pagada o cancelada.')
        return redirect('reserva_detalle', pk=pk)
    
    access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', None)
    if not access_token or access_token == 'TU_ACCESS_TOKEN_AQUI':
        messages.error(request, 'MercadoPago no está configurado correctamente. Contacte al administrador.')
        return redirect('reserva_detalle', pk=pk)
    
    try:
        sdk = mercadopago.SDK(access_token)
        
        preference_data = {
            "items": [
                {
                    "title": f"Reserva #{reserva.id} - {reserva.cancha.nombre}",
                    "description": f"Reserva de cancha del {reserva.fecha_hora_inicio.strftime('%d/%m/%Y')} de {reserva.fecha_hora_inicio.strftime('%H:%M')} a {reserva.fecha_hora_fin.strftime('%H:%M')}",
                    "quantity": 1,
                    "currency_id": "ARS",
                    "unit_price": float(pago.monto_total)
                }
            ],
            "payer": {
                "name": reserva.cliente.nombre,
                "surname": reserva.cliente.apellido,
                "email": reserva.cliente.email
            },
            "external_reference": str(reserva.id),
            "statement_descriptor": "RESERVA CANCHA"
        }
        
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response["status"] == 201:
            preference = preference_response["response"]
            
            pago.mp_preference_id = preference["id"]
            pago.save()
            
            init_point = preference.get("init_point")
            if init_point:
                return redirect(init_point)
            else:
                messages.error(request, 'Error al obtener la URL de pago de MercadoPago.')
                return redirect('reserva_detalle', pk=pk)
        else:
            error_msg = preference_response.get("response", {}).get("message", "Error desconocido")
            messages.error(request, f'Error al crear la preferencia de pago: {error_msg}')
            return redirect('reserva_detalle', pk=pk)
            
    except Exception as e:
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('reserva_detalle', pk=pk)


