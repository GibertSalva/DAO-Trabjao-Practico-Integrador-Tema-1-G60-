from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Cliente, Cancha, TipoCancha, Reserva, Servicio, Torneo, Pago

# Aca creamos las vistas para la app 'reservas'

# ========== VISTA PRINCIPAL ==========

def home(request):
    """Página principal del sistema"""
    context = {
        'total_clientes': Cliente.objects.count(),
        'total_canchas': Cancha.objects.count(),
        'reservas_activas': Reserva.objects.filter(estado='CONFIRMADA').count(),
        'reservas_pendientes': Reserva.objects.filter(estado='PENDIENTE').count(),
    }
    return render(request, 'reservas/home.html', context)

# ========== VISTAS DE CLIENTES ==========

def cliente_lista(request):
    """Listar todos los clientes"""
    clientes = Cliente.objects.all().order_by('apellido', 'nombre')
    return render(request, 'reservas/cliente_lista.html', {'clientes': clientes})

def cliente_crear(request):
    """Crear un nuevo cliente"""
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.create(
                nombre=request.POST['nombre'],
                apellido=request.POST['apellido'],
                dni=request.POST['dni'],
                email=request.POST['email'],
                telefono=request.POST['telefono']
            )
            messages.success(request, f'Cliente {cliente.nombre} {cliente.apellido} creado exitosamente.')
            return redirect('cliente_lista')
        except Exception as e:
            messages.error(request, f'Error al crear cliente: {str(e)}')
    
    return render(request, 'reservas/cliente_form.html')

def cliente_editar(request, pk):
    """Editar un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        try:
            cliente.nombre = request.POST['nombre']
            cliente.apellido = request.POST['apellido']
            cliente.dni = request.POST['dni']
            cliente.email = request.POST['email']
            cliente.telefono = request.POST['telefono']
            cliente.save()
            messages.success(request, f'Cliente {cliente.nombre} {cliente.apellido} actualizado exitosamente.')
            return redirect('cliente_lista')
        except Exception as e:
            messages.error(request, f'Error al actualizar cliente: {str(e)}')
    
    return render(request, 'reservas/cliente_form.html', {'cliente': cliente})

def cliente_eliminar(request, pk):
    """Eliminar un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        nombre_completo = f'{cliente.nombre} {cliente.apellido}'
        cliente.delete()
        messages.success(request, f'Cliente {nombre_completo} eliminado exitosamente.')
        return redirect('cliente_lista')
    
    return render(request, 'reservas/cliente_confirmar_eliminar.html', {'cliente': cliente})

def cliente_detalle(request, pk):
    """Ver detalle de un cliente y sus reservas"""
    cliente = get_object_or_404(Cliente, pk=pk)
    reservas = cliente.reservas.all().order_by('-fecha_hora_inicio')
    return render(request, 'reservas/cliente_detalle.html', {
        'cliente': cliente,
        'reservas': reservas
    })

# ========== VISTAS DE CANCHAS ==========

def cancha_lista(request):
    """Listar todas las canchas"""
    canchas = Cancha.objects.all().select_related('tipo_cancha').order_by('nombre')
    tipos_cancha = TipoCancha.objects.all()
    return render(request, 'reservas/cancha_lista.html', {
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
    return render(request, 'reservas/cancha_form.html', {'tipos_cancha': tipos_cancha})

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
    return render(request, 'reservas/cancha_form.html', {
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
    
    return render(request, 'reservas/cancha_confirmar_eliminar.html', {'cancha': cancha})

def cancha_detalle(request, pk):
    """Ver detalle de una cancha y sus reservas"""
    cancha = get_object_or_404(Cancha, pk=pk)
    reservas = cancha.reservas.all().order_by('-fecha_hora_inicio')[:10]
    return render(request, 'reservas/cancha_detalle.html', {
        'cancha': cancha,
        'reservas': reservas
    })

# ========== VISTAS DE RESERVAS ==========

def reserva_lista(request):
    """Listar todas las reservas con filtros opcionales"""
    reservas = Reserva.objects.all().select_related('cliente', 'cancha', 'torneo').order_by('-fecha_hora_inicio')
    
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
    
    clientes = Cliente.objects.all().order_by('apellido', 'nombre')
    canchas = Cancha.objects.all().order_by('nombre')
    
    return render(request, 'reservas/reserva_lista.html', {
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
    
    return render(request, 'reservas/reserva_form.html', {
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
    
    return render(request, 'reservas/reserva_form.html', {
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
    
    return render(request, 'reservas/reserva_confirmar_eliminar.html', {'reserva': reserva})

def reserva_detalle(request, pk):
    """Ver detalle completo de una reserva"""
    reserva = get_object_or_404(Reserva, pk=pk)
    return render(request, 'reservas/reserva_detalle.html', {'reserva': reserva})

# ========== FUNCIONES AUXILIARES PARA PERMISOS ==========

def es_administrador(user):
    """Verifica si el usuario es administrador (staff)"""
    return user.is_staff or user.is_superuser

# ========== VISTAS DE AUTENTICACIÓN ==========

def registro_view(request):
    """Registro de nuevos usuarios clientes"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Datos del usuario
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            password2 = request.POST['password2']
            
            # Datos del cliente
            nombre = request.POST['nombre']
            apellido = request.POST['apellido']
            dni = request.POST['dni']
            telefono = request.POST['telefono']
            
            # Validaciones
            if password != password2:
                messages.error(request, 'Las contraseñas no coinciden.')
                return redirect('registro')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya está en uso.')
                return redirect('registro')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'El email ya está registrado.')
                return redirect('registro')
            
            if Cliente.objects.filter(dni=dni).exists():
                messages.error(request, 'El DNI ya está registrado.')
                return redirect('registro')
            
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellido
            )
            
            # Crear cliente asociado
            cliente = Cliente.objects.create(
                usuario=user,
                nombre=nombre,
                apellido=apellido,
                dni=dni,
                email=email,
                telefono=telefono
            )
            
            # Iniciar sesión automáticamente
            login(request, user)
            messages.success(request, f'¡Bienvenido {nombre}! Tu cuenta ha sido creada exitosamente.')
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')
    
    return render(request, 'reservas/registro.html')

def login_view(request):
    """Inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido de vuelta, {user.first_name or user.username}!')
            
            # Redirigir a la página solicitada o a home
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'reservas/login.html')

def logout_view(request):
    """Cierre de sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')

@login_required
def perfil_view(request):
    """Perfil del usuario"""
    try:
        cliente = request.user.cliente
    except:
        cliente = None
    
    # Obtener reservas del cliente
    if cliente:
        reservas = cliente.reservas.all().order_by('-fecha_hora_inicio')[:10]
    else:
        reservas = []
    
    context = {
        'cliente': cliente,
        'reservas': reservas,
    }
    return render(request, 'reservas/perfil.html', context)

@login_required
def editar_perfil_view(request):
    """Editar perfil del usuario"""
    try:
        cliente = request.user.cliente
    except:
        messages.error(request, 'No tienes un perfil de cliente asociado.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            # Actualizar datos del usuario
            request.user.first_name = request.POST['nombre']
            request.user.last_name = request.POST['apellido']
            request.user.email = request.POST['email']
            request.user.save()
            
            # Actualizar datos del cliente
            cliente.nombre = request.POST['nombre']
            cliente.apellido = request.POST['apellido']
            cliente.email = request.POST['email']
            cliente.telefono = request.POST['telefono']
            cliente.save()
            
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('perfil')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el perfil: {str(e)}')
    
    return render(request, 'reservas/editar_perfil.html', {'cliente': cliente})

@login_required
def mis_reservas_view(request):
    """Reservas del usuario autenticado"""
    try:
        cliente = request.user.cliente
        reservas = cliente.reservas.all().order_by('-fecha_hora_inicio')
    except:
        messages.warning(request, 'No tienes un perfil de cliente asociado.')
        reservas = []
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        reservas = reservas.filter(estado=estado)
    
    return render(request, 'reservas/mis_reservas.html', {
        'reservas': reservas,
        'estados': Reserva.ESTADO_CHOICES
    })
