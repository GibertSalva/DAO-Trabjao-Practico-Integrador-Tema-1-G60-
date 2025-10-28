from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Cliente, Cancha, TipoCancha, Reserva, Servicio, Torneo, Pago, Equipo, Partido

# Aca creamos las vistas para la app 'reservas'

# ========== VISTA PRINCIPAL ==========

def home(request):
    """Página principal del sistema"""
    # Calcular torneos vigentes (activos o próximos)
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

# ========== VISTAS DE CLIENTES ==========

def cliente_lista(request):
    """Listar todos los clientes con paginación y búsqueda"""
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
    """Crear un nuevo cliente"""
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

# ========== VISTAS DE CANCHAS ==========

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
                precio_por_hora=request.POST['precio_por_hora']
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

# ========== VISTAS DE RESERVAS ==========

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
        try:
            cliente = get_object_or_404(Cliente, pk=request.POST['cliente'])
            cancha = get_object_or_404(Cancha, pk=request.POST['cancha'])
            
            # Convertir fechas
            fecha_inicio = datetime.fromisoformat(request.POST['fecha_hora_inicio'])
            fecha_fin = datetime.fromisoformat(request.POST['fecha_hora_fin'])
            
            # Validar que la fecha de fin sea posterior a la de inicio
            if fecha_fin <= fecha_inicio:
                messages.error(request, 'La fecha de fin debe ser posterior a la fecha de inicio.')
                return redirect('reserva_crear')
            
            # Validar disponibilidad de la cancha
            reservas_conflicto = Reserva.objects.filter(
                cancha=cancha,
                estado__in=['PENDIENTE', 'PAGADA']
            ).filter(
                Q(fecha_hora_inicio__lt=fecha_fin) & Q(fecha_hora_fin__gt=fecha_inicio)
            )
            
            if reservas_conflicto.exists():
                messages.error(request, 'La cancha no está disponible en el horario seleccionado.')
                return redirect('reserva_crear')
            
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

# ========== VISTA DE REPORTES ==========

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
    
    # ===== REPORTE 1: Listado de reservas por cliente =====
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
    
    # Ordenar por número de reservas (de mayor a menor)
    clientes_con_reservas = sorted(
        clientes_con_reservas,
        key=lambda x: (x['num_reservas'], x['total_gasto']),
        reverse=True
    )
    
    # ===== REPORTE 2: Reservas por cancha en el período =====
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
    
    # Ordenar por número de reservas, total de horas e ingresos (de mayor a menor)
    canchas_con_reservas = sorted(
        canchas_con_reservas,
        key=lambda x: (x['num_reservas'], x['total_horas'], x['total_ingresos']),
        reverse=True
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
    """Genera un PDF con los reportes del mes seleccionado"""
    # TODO: Implementar generación de PDF
    return HttpResponse("Funcionalidad de PDF en desarrollo", content_type="text/plain")


# ========== VISTAS DE TORNEOS ==========

def torneo_lista(request):
    """Listar todos los torneos con paginación"""
    # Obtener torneos y ordenarlos
    torneos_list = Torneo.objects.all().order_by('-fecha_inicio')
    
    # Actualizar estados de torneos según fechas
    hoy = timezone.now().date()
    for torneo in torneos_list:
        estado_anterior = torneo.estado
        
        # Si pasó la fecha fin, debe estar FINALIZADO
        if hoy > torneo.fecha_fin and torneo.estado != 'FINALIZADO':
            torneo.estado = 'FINALIZADO'
            torneo.save()
        # Si está entre las fechas y tiene partidos, debe estar EN_CURSO
        elif torneo.fecha_inicio <= hoy <= torneo.fecha_fin and torneo.estado != 'FINALIZADO':
            if torneo.partidos.exists() and torneo.estado == 'INSCRIPCION':
                torneo.estado = 'EN_CURSO'
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
                deporte=request.POST.get('deporte', 'Fútbol 5'),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                premio=request.POST.get('premio', ''),
                estado=request.POST.get('estado', 'INSCRIPCION'),
                costo_inscripcion=request.POST.get('costo_inscripcion', 0) or 0,
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
    
    if torneo.fecha_inicio <= hoy <= torneo.fecha_fin and torneo.estado != 'FINALIZADO':
        # Si está entre las fechas y tiene fixture, debe estar EN_CURSO
        if torneo.partidos.exists() and torneo.estado == 'INSCRIPCION':
            torneo.estado = 'EN_CURSO'
            torneo.save()
    elif hoy > torneo.fecha_fin and torneo.estado != 'FINALIZADO':
        # Si pasó la fecha fin, debería estar FINALIZADO
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
    total_partidos = torneo.partidos.count()
    partidos_completados = torneo.partidos.filter(estado='FINALIZADO').count()
    
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
        'total_partidos': total_partidos,
        'partidos_completados': partidos_completados,
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
            torneo.deporte = request.POST.get('deporte', 'Fútbol 5')
            torneo.fecha_inicio = fecha_inicio
            torneo.fecha_fin = fecha_fin
            torneo.premio = request.POST.get('premio', '')
            torneo.estado = request.POST.get('estado', 'INSCRIPCION')
            torneo.costo_inscripcion = request.POST.get('costo_inscripcion', 0) or 0
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
    
    # Actualizar estado según fechas
    hoy = timezone.now().date()
    if torneo.fecha_inicio <= hoy and torneo.estado == 'INSCRIPCION':
        if torneo.partidos.exists():
            torneo.estado = 'EN_CURSO'
            torneo.save()
    
    # Validar que el torneo esté en inscripción Y no haya comenzado
    if torneo.estado != 'INSCRIPCION' or torneo.fecha_inicio <= hoy:
        messages.error(request, 'No se pueden inscribir equipos. El torneo ya comenzó o no está abierto para inscripciones.')
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
    
    # Validar que el torneo esté en inscripción Y no haya comenzado
    hoy = timezone.now().date()
    if torneo.estado != 'INSCRIPCION' or torneo.fecha_inicio <= hoy:
        messages.error(request, 'No se pueden desinscribir equipos. El torneo ya comenzó o no está abierto para inscripciones.')
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
            
            messages.success(request, f'Resultado registrado. Ganador: {partido.ganador.nombre}')
            return redirect('torneo_fixture', pk=partido.torneo.pk)
            
        except Exception as e:
            messages.error(request, f'Error al registrar resultado: {str(e)}')
    
    context = {
        'partido': partido,
        'torneo': partido.torneo,
    }
    return render(request, 'reservas/torneos/registrar_resultado.html', context)


# ========== VISTAS DE EQUIPOS (Independientes) ==========

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


