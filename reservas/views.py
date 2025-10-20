from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Cliente, Cancha, TipoCancha, Reserva, Servicio, Torneo, Pago

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
        'reservas_activas': Reserva.objects.filter(estado='CONFIRMADA').count(),
        'reservas_pendientes': Reserva.objects.filter(estado='PENDIENTE').count(),
        'torneos_vigentes': torneos_vigentes,
    }
    return render(request, 'reservas/home.html', context)

# ========== VISTAS DE CLIENTES ==========

def cliente_lista(request):
    """Listar todos los clientes"""
    clientes = Cliente.objects.all().order_by('id')
    return render(request, 'reservas/clientes/lista.html', {'clientes': clientes})

def cliente_crear(request):
    """Crear un nuevo cliente"""
    if request.method == 'POST':
        try:
            # Verificar si el DNI ya existe
            dni = request.POST['dni']
            if Cliente.objects.filter(dni=dni).exists():
                messages.error(request, f'Ya existe un cliente con el DNI {dni}. Por favor, verifica los datos.')
                return render(request, 'reservas/clientes/form.html')
            
            # Verificar si el email ya existe
            email = request.POST['email']
            if Cliente.objects.filter(email=email).exists():
                messages.error(request, f'Ya existe un cliente con el email {email}. Por favor, usa otro email.')
                return render(request, 'reservas/clientes/form.html')
            
            cliente = Cliente.objects.create(
                nombre=request.POST['nombre'],
                apellido=request.POST['apellido'],
                dni=dni,
                email=email,
                telefono=request.POST['telefono']
            )
            messages.success(request, f'Cliente {cliente.nombre} {cliente.apellido} creado exitosamente.')
            return redirect('cliente_lista')
        except Exception as e:
            messages.error(request, f'Error al crear cliente: {str(e)}')
    
    return render(request, 'reservas/clientes/form.html')

def cliente_editar(request, pk):
    """Editar un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        try:
            # Verificar si el DNI ya existe en otro cliente
            dni = request.POST['dni']
            if Cliente.objects.filter(dni=dni).exclude(pk=pk).exists():
                messages.error(request, f'Ya existe otro cliente con el DNI {dni}. Por favor, verifica los datos.')
                return render(request, 'reservas/clientes/form.html', {'cliente': cliente})
            
            # Verificar si el email ya existe en otro cliente
            email = request.POST['email']
            if Cliente.objects.filter(email=email).exclude(pk=pk).exists():
                messages.error(request, f'Ya existe otro cliente con el email {email}. Por favor, usa otro email.')
                return render(request, 'reservas/clientes/form.html', {'cliente': cliente})
            
            cliente.nombre = request.POST['nombre']
            cliente.apellido = request.POST['apellido']
            cliente.dni = dni
            cliente.email = email
            cliente.telefono = request.POST['telefono']
            cliente.save()
            messages.success(request, f'Cliente {cliente.nombre} {cliente.apellido} actualizado exitosamente.')
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
    """Listar todas las canchas"""
    canchas = Cancha.objects.all().select_related('tipo_cancha').order_by('id')
    tipos_cancha = TipoCancha.objects.all()
    return render(request, 'reservas/canchas/lista.html', {
        'canchas': canchas,
        'tipos_cancha': tipos_cancha
    })

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
    """Listar todas las reservas con filtros opcionales"""
    reservas = Reserva.objects.all().select_related('cliente', 'cancha', 'torneo').order_by('-id')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        reservas = reservas.filter(estado=estado)
    
    cliente_id = request.GET.get('cliente')
    if cliente_id:
        reservas = reservas.filter(cliente_id=cliente_id)
    
    cancha_id = request.GET.get('cancha')
    if cancha_id:
        reservas = reservas.filter(cancha_id=cancha_id)
    
    clientes = Cliente.objects.all().order_by('id')
    canchas = Cancha.objects.all().order_by('id')
    
    return render(request, 'reservas/reservas/lista.html', {
        'reservas': reservas,
        'clientes': clientes,
        'canchas': canchas,
        'estados': Reserva.ESTADO_CHOICES
    })

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
                estado__in=['PENDIENTE', 'CONFIRMADA']
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
    
    clientes = Cliente.objects.all().order_by('apellido', 'nombre')
    canchas = Cancha.objects.all().order_by('nombre')
    servicios = Servicio.objects.all()
    torneos = Torneo.objects.all()
    
    return render(request, 'reservas/reservas/form.html', {
        'clientes': clientes,
        'canchas': canchas,
        'servicios': servicios,
        'torneos': torneos,
        'estados': Reserva.ESTADO_CHOICES
    })

def reserva_editar(request, pk):
    """Editar una reserva existente"""
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        try:
            reserva.estado = request.POST['estado']
            
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
            
            # Recalcular monto del pago
            if hasattr(reserva, 'pago'):
                horas = (reserva.fecha_hora_fin - reserva.fecha_hora_inicio).total_seconds() / 3600
                monto_cancha = float(reserva.cancha.precio_por_hora) * horas
                monto_servicios = sum(float(s.costo_adicional) for s in reserva.servicios.all())
                reserva.pago.monto_total = monto_cancha + monto_servicios
                reserva.pago.save()
            
            messages.success(request, 'Reserva actualizada exitosamente.')
            return redirect('reserva_lista')
            
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
    return render(request, 'reservas/reservas/detalle.html', {'reserva': reserva})

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
    
    # ===== REPORTE 3: Canchas más utilizadas =====
    canchas_ranking = sorted(
        [c for c in canchas_con_reservas],
        key=lambda x: (x['num_reservas'], x['total_horas']),
        reverse=True
    )
    
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
    """Listar todos los torneos"""
    # Obtener torneos y ordenarlos
    torneos = Torneo.objects.all().order_by('-fecha_inicio')
    
    # Clasificar torneos por estado
    hoy = timezone.now().date()
    torneos_activos = []
    torneos_proximos = []
    torneos_finalizados = []
    
    for torneo in torneos:
        if torneo.fecha_inicio <= hoy <= torneo.fecha_fin:
            torneos_activos.append(torneo)
        elif torneo.fecha_inicio > hoy:
            torneos_proximos.append(torneo)
        else:
            torneos_finalizados.append(torneo)
    
    context = {
        'torneos_activos': torneos_activos,
        'torneos_proximos': torneos_proximos,
        'torneos_finalizados': torneos_finalizados,
        'total_torneos': torneos.count(),
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
                max_equipos=request.POST.get('max_equipos', None) or None,
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
    
    # Obtener reservas asociadas al torneo
    reservas = Reserva.objects.filter(torneo=torneo).select_related('cliente', 'cancha').order_by('fecha_hora_inicio')
    
    # Calcular estadísticas
    total_reservas = reservas.count()
    reservas_confirmadas = reservas.filter(estado='CONFIRMADA').count()
    reservas_pendientes = reservas.filter(estado='PENDIENTE').count()
    
    # Calcular ingresos del torneo (inscripciones + reservas)
    ingresos_inscripciones = float(torneo.costo_inscripcion or 0) * total_reservas
    ingresos_reservas = sum(float(r.calcular_costo_total()) for r in reservas.filter(estado='CONFIRMADA'))
    ingresos_totales = ingresos_inscripciones + ingresos_reservas
    
    # Estado del torneo
    hoy = timezone.now().date()
    if torneo.fecha_inicio <= hoy <= torneo.fecha_fin:
        estado = 'EN CURSO'
        estado_clase = 'badge-success'
    elif torneo.fecha_inicio > hoy:
        estado = 'PRÓXIMO'
        estado_clase = 'badge-info'
    else:
        estado = 'FINALIZADO'
        estado_clase = 'badge-ghost'
    
    # Calcular días restantes
    if estado == 'PRÓXIMO':
        dias_restantes = (torneo.fecha_inicio - hoy).days
    elif estado == 'EN CURSO':
        dias_restantes = (torneo.fecha_fin - hoy).days
    else:
        dias_restantes = 0
    
    context = {
        'torneo': torneo,
        'reservas': reservas,
        'total_reservas': total_reservas,
        'reservas_confirmadas': reservas_confirmadas,
        'reservas_pendientes': reservas_pendientes,
        'ingresos_inscripciones': ingresos_inscripciones,
        'ingresos_reservas': ingresos_reservas,
        'ingresos_totales': ingresos_totales,
        'estado': estado,
        'estado_clase': estado_clase,
        'dias_restantes': dias_restantes,
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
            torneo.max_equipos = request.POST.get('max_equipos', None) or None
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

