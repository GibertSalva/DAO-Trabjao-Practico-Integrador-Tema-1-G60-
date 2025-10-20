# -*- coding: utf-8 -*-
"""
Script para poblar la base de datos con datos de prueba
Ejecutar con: python poblar_db.py
"""

import os
import django
import sys
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canchas_project.settings')
django.setup()

from django.utils import timezone
from reservas.models import TipoCancha, Cliente, Cancha, Servicio, Torneo, Reserva, Pago

def limpiar_datos():
    """Elimina todos los datos existentes"""
    print("Limpiando datos existentes...")
    Pago.objects.all().delete()
    Reserva.objects.all().delete()
    Torneo.objects.all().delete()
    Servicio.objects.all().delete()
    Cancha.objects.all().delete()
    Cliente.objects.all().delete()
    TipoCancha.objects.all().delete()
    print("Base de datos limpiada.")

def crear_tipos_cancha():
    """Crea tipos de cancha"""
    print("\n1. Creando tipos de cancha...")
    tipos = [
        {
            'nombre': 'Futbol 5',
            'descripcion': 'Cancha de futbol para 5 jugadores por equipo. Dimensiones reducidas.'
        },
        {
            'nombre': 'Futbol 7',
            'descripcion': 'Cancha de futbol para 7 jugadores por equipo. Tamanio intermedio.'
        },
        {
            'nombre': 'Futbol 11',
            'descripcion': 'Cancha de futbol profesional para 11 jugadores por equipo.'
        },
        {
            'nombre': 'Paddle',
            'descripcion': 'Cancha de paddle con paredes de vidrio. Superficie de cesped sintetico.'
        },
        {
            'nombre': 'Tenis',
            'descripcion': 'Cancha de tenis reglamentaria. Superficie de polvo de ladrillo.'
        },
    ]
    
    tipos_creados = []
    for tipo_data in tipos:
        tipo = TipoCancha.objects.create(**tipo_data)
        tipos_creados.append(tipo)
        print(f"  - {tipo.nombre}")
    
    return tipos_creados

def crear_clientes():
    """Crea clientes de prueba"""
    print("\n2. Creando clientes...")
    clientes = [
        {
            'nombre': 'Juan',
            'apellido': 'Perez',
            'dni': '35123456',
            'email': 'juan.perez@email.com',
            'telefono': '11-4567-8901'
        },
        {
            'nombre': 'Maria',
            'apellido': 'Garcia',
            'dni': '38234567',
            'email': 'maria.garcia@email.com',
            'telefono': '11-5678-9012'
        },
        {
            'nombre': 'Carlos',
            'apellido': 'Rodriguez',
            'dni': '32345678',
            'email': 'carlos.rodriguez@email.com',
            'telefono': '11-6789-0123'
        },
        {
            'nombre': 'Laura',
            'apellido': 'Martinez',
            'dni': '40456789',
            'email': 'laura.martinez@email.com',
            'telefono': '11-7890-1234'
        },
        {
            'nombre': 'Diego',
            'apellido': 'Fernandez',
            'dni': '37567890',
            'email': 'diego.fernandez@email.com',
            'telefono': '11-8901-2345'
        },
        {
            'nombre': 'Ana',
            'apellido': 'Lopez',
            'dni': '41678901',
            'email': 'ana.lopez@email.com',
            'telefono': '11-9012-3456'
        },
        {
            'nombre': 'Roberto',
            'apellido': 'Gonzalez',
            'dni': '34789012',
            'email': 'roberto.gonzalez@email.com',
            'telefono': '11-2345-6789'
        },
        {
            'nombre': 'Sofia',
            'apellido': 'Sanchez',
            'dni': '39890123',
            'email': 'sofia.sanchez@email.com',
            'telefono': '11-3456-7890'
        },
        {
            'nombre': 'Miguel',
            'apellido': 'Ramirez',
            'dni': '36901234',
            'email': 'miguel.ramirez@email.com',
            'telefono': '11-4567-8902'
        },
        {
            'nombre': 'Valentina',
            'apellido': 'Torres',
            'dni': '42012345',
            'email': 'valentina.torres@email.com',
            'telefono': '11-5678-9013'
        },
    ]
    
    clientes_creados = []
    for cliente_data in clientes:
        cliente = Cliente.objects.create(**cliente_data)
        clientes_creados.append(cliente)
        print(f"  - {cliente.nombre} {cliente.apellido} (DNI: {cliente.dni})")
    
    return clientes_creados

def crear_canchas(tipos_cancha):
    """Crea canchas"""
    print("\n3. Creando canchas...")
    
    # Mapeo de tipos
    tipo_futbol5 = tipos_cancha[0]
    tipo_futbol7 = tipos_cancha[1]
    tipo_futbol11 = tipos_cancha[2]
    tipo_paddle = tipos_cancha[3]
    tipo_tenis = tipos_cancha[4]
    
    canchas = [
        {
            'nombre': 'Cancha Central',
            'tipo_cancha': tipo_futbol11,
            'precio_por_hora': Decimal('15000.00'),
            'capacidad_personas': 22,
            'activa': True
        },
        {
            'nombre': 'Cancha 1 - Futbol 5',
            'tipo_cancha': tipo_futbol5,
            'precio_por_hora': Decimal('8000.00'),
            'capacidad_personas': 10,
            'activa': True
        },
        {
            'nombre': 'Cancha 2 - Futbol 5',
            'tipo_cancha': tipo_futbol5,
            'precio_por_hora': Decimal('8000.00'),
            'capacidad_personas': 10,
            'activa': True
        },
        {
            'nombre': 'Cancha 3 - Futbol 7',
            'tipo_cancha': tipo_futbol7,
            'precio_por_hora': Decimal('12000.00'),
            'capacidad_personas': 14,
            'activa': True
        },
        {
            'nombre': 'Cancha 4 - Futbol 7',
            'tipo_cancha': tipo_futbol7,
            'precio_por_hora': Decimal('12000.00'),
            'capacidad_personas': 14,
            'activa': True
        },
        {
            'nombre': 'Paddle 1',
            'tipo_cancha': tipo_paddle,
            'precio_por_hora': Decimal('6000.00'),
            'capacidad_personas': 4,
            'activa': True
        },
        {
            'nombre': 'Paddle 2',
            'tipo_cancha': tipo_paddle,
            'precio_por_hora': Decimal('6000.00'),
            'capacidad_personas': 4,
            'activa': True
        },
        {
            'nombre': 'Tenis Principal',
            'tipo_cancha': tipo_tenis,
            'precio_por_hora': Decimal('7000.00'),
            'capacidad_personas': 4,
            'activa': True
        },
    ]
    
    canchas_creadas = []
    for cancha_data in canchas:
        cancha = Cancha.objects.create(**cancha_data)
        canchas_creadas.append(cancha)
        print(f"  - {cancha.nombre} ({cancha.tipo_cancha.nombre}) - ${cancha.precio_por_hora}/h")
    
    return canchas_creadas

def crear_servicios():
    """Crea servicios adicionales"""
    print("\n4. Creando servicios...")
    servicios = [
        {
            'nombre': 'Alquiler de pelotas',
            'costo_adicional': Decimal('500.00'),
            'descripcion': 'Pelota oficial para el deporte elegido',
            'activo': True
        },
        {
            'nombre': 'Iluminacion nocturna',
            'costo_adicional': Decimal('1500.00'),
            'descripcion': 'Iluminacion LED de alta intensidad',
            'activo': True
        },
        {
            'nombre': 'Vestuarios premium',
            'costo_adicional': Decimal('800.00'),
            'descripcion': 'Acceso a vestuarios con duchas y lockers',
            'activo': True
        },
        {
            'nombre': 'Arbitro profesional',
            'costo_adicional': Decimal('3000.00'),
            'descripcion': 'Arbitro certificado para el partido',
            'activo': True
        },
        {
            'nombre': 'Video grabacion',
            'costo_adicional': Decimal('2500.00'),
            'descripcion': 'Grabacion profesional del partido con 2 camaras',
            'activo': True
        },
        {
            'nombre': 'Catering basico',
            'costo_adicional': Decimal('4000.00'),
            'descripcion': 'Bebidas frias y snacks para el equipo',
            'activo': True
        },
    ]
    
    servicios_creados = []
    for servicio_data in servicios:
        servicio = Servicio.objects.create(**servicio_data)
        servicios_creados.append(servicio)
        print(f"  - {servicio.nombre} (+${servicio.costo_adicional})")
    
    return servicios_creados

def crear_torneos():
    """Crea torneos"""
    print("\n5. Creando torneos...")
    hoy = datetime.now().date()
    
    torneos = [
        {
            'nombre': 'Torneo Apertura 2025',
            'fecha_inicio': hoy + timedelta(days=10),
            'fecha_fin': hoy + timedelta(days=40),
            'reglamento': 'Torneo de futbol 5. Sistema de todos contra todos. Partidos de 50 minutos.',
            'activo': True
        },
        {
            'nombre': 'Copa de Verano',
            'fecha_inicio': hoy + timedelta(days=60),
            'fecha_fin': hoy + timedelta(days=90),
            'reglamento': 'Torneo de futbol 7. Fase de grupos y eliminacion directa. Final a dos partidos.',
            'activo': True
        },
        {
            'nombre': 'Torneo Relampago Paddle',
            'fecha_inicio': hoy + timedelta(days=5),
            'fecha_fin': hoy + timedelta(days=6),
            'reglamento': 'Torneo express de paddle. Formato americano. Duracion: 2 dias.',
            'activo': True
        },
    ]
    
    torneos_creados = []
    for torneo_data in torneos:
        torneo = Torneo.objects.create(**torneo_data)
        torneos_creados.append(torneo)
        print(f"  - {torneo.nombre} ({torneo.fecha_inicio} al {torneo.fecha_fin})")
    
    return torneos_creados

def crear_reservas(clientes, canchas, servicios, torneos):
    """Crea reservas de prueba"""
    print("\n6. Creando reservas...")
    
    # Usar fecha base en octubre 2025 para que aparezca en reportes
    hoy = timezone.make_aware(datetime(2025, 10, 15, 12, 0))  # 15 de octubre de 2025 al mediodía
    reservas_creadas = []
    
    # Reservas pasadas (confirmadas y pagadas)
    reservas_pasadas = [
        {
            'cliente': clientes[0],
            'cancha': canchas[1],
            'fecha_hora_inicio': timezone.make_aware(datetime(2025, 10, 12, 10, 0)),  # 12 oct 10:00
            'fecha_hora_fin': timezone.make_aware(datetime(2025, 10, 12, 12, 0)),     # 12 oct 12:00
            'estado': 'CONFIRMADA',
            'observaciones': 'Partido amistoso. Sin problemas.',
            'servicios': [servicios[0], servicios[1]],
        },
        {
            'cliente': clientes[1],
            'cancha': canchas[3],
            'fecha_hora_inicio': timezone.make_aware(datetime(2025, 10, 13, 14, 0)),  # 13 oct 14:00
            'fecha_hora_fin': timezone.make_aware(datetime(2025, 10, 13, 16, 0)),     # 13 oct 16:00
            'estado': 'CONFIRMADA',
            'observaciones': 'Entrenamiento de equipo juvenil.',
            'servicios': [servicios[3]],
        },
        {
            'cliente': clientes[2],
            'cancha': canchas[5],
            'fecha_hora_inicio': timezone.make_aware(datetime(2025, 10, 14, 9, 0)),   # 14 oct 09:00
            'fecha_hora_fin': timezone.make_aware(datetime(2025, 10, 14, 10, 0)),     # 14 oct 10:00
            'estado': 'CONFIRMADA',
            'observaciones': 'Clase de paddle para principiantes.',
            'servicios': [servicios[0]],
        },
    ]
    
    # Reservas futuras (pendientes y confirmadas)
    reservas_futuras = [
        {
            'cliente': clientes[3],
            'cancha': canchas[0],
            'fecha_hora_inicio': timezone.make_aware(datetime(2025, 10, 18, 10, 0)),  # 18 oct 10:00
            'fecha_hora_fin': timezone.make_aware(datetime(2025, 10, 18, 12, 0)),     # 18 oct 12:00
            'estado': 'CONFIRMADA',
            'observaciones': 'Partido importante. Necesitamos todo listo.',
            'servicios': [servicios[1], servicios[3], servicios[4]],
            'torneo': torneos[0],
        },
        {
            'cliente': clientes[4],
            'cancha': canchas[2],
            'fecha_hora_inicio': timezone.make_aware(datetime(2025, 10, 19, 14, 0)),  # 19 oct 14:00
            'fecha_hora_fin': timezone.make_aware(datetime(2025, 10, 19, 16, 0)),     # 19 oct 16:00
            'estado': 'PENDIENTE',
            'observaciones': 'Esperando confirmacion de pago.',
            'servicios': [servicios[0], servicios[1]],
        },
        {
            'cliente': clientes[5],
            'cancha': canchas[6],
            'fecha_hora_inicio': timezone.make_aware(datetime(2025, 10, 20, 9, 0)),   # 20 oct 09:00
            'fecha_hora_fin': timezone.make_aware(datetime(2025, 10, 20, 10, 0)),     # 20 oct 10:00
            'estado': 'CONFIRMADA',
            'observaciones': 'Partidos de paddle dobles.',
            'servicios': [],
        },
        {
            'cliente': clientes[6],
            'cancha': canchas[4],
            'fecha_hora_inicio': timezone.make_aware(datetime(2025, 10, 21, 16, 0)),  # 21 oct 16:00
            'fecha_hora_fin': timezone.make_aware(datetime(2025, 10, 21, 18, 0)),     # 21 oct 18:00
            'estado': 'CONFIRMADA',
            'observaciones': 'Amistoso entre equipos locales.',
            'servicios': [servicios[1], servicios[5]],
        },
        {
            'cliente': clientes[7],
            'cancha': canchas[7],
            'fecha_hora_inicio': timezone.make_aware(datetime(2025, 10, 22, 8, 0)),   # 22 oct 08:00
            'fecha_hora_fin': timezone.make_aware(datetime(2025, 10, 22, 10, 0)),     # 22 oct 10:00
            'estado': 'PENDIENTE',
            'observaciones': 'Clase de tenis individual.',
            'servicios': [servicios[0]],
        },
        {
            'cliente': clientes[8],
            'cancha': canchas[1],
            'fecha_hora_inicio': timezone.make_aware(datetime(2025, 10, 23, 19, 0)),  # 23 oct 19:00
            'fecha_hora_fin': timezone.make_aware(datetime(2025, 10, 23, 21, 0)),     # 23 oct 21:00
            'estado': 'CONFIRMADA',
            'observaciones': 'Partido nocturno con iluminacion.',
            'servicios': [servicios[1]],
        },
        {
            'cliente': clientes[9],
            'cancha': canchas[3],
            'fecha_hora_inicio': timezone.make_aware(datetime(2025, 10, 24, 11, 0)),  # 24 oct 11:00
            'fecha_hora_fin': timezone.make_aware(datetime(2025, 10, 24, 13, 0)),     # 24 oct 13:00
            'estado': 'PENDIENTE',
            'observaciones': 'Celebracion de cumpleanos. Partido especial.',
            'servicios': [servicios[0], servicios[5]],
        },
        {
            'cliente': clientes[0],
            'cancha': canchas[5],
            'fecha_hora_inicio': timezone.make_aware(datetime(2025, 10, 25, 10, 0)),  # 25 oct 10:00
            'fecha_hora_fin': timezone.make_aware(datetime(2025, 10, 25, 11, 0)),     # 25 oct 11:00
            'estado': 'CONFIRMADA',
            'observaciones': 'Torneo relampago de paddle.',
            'servicios': [],
            'torneo': torneos[2],
        },
    ]
    
    todas_las_reservas = reservas_pasadas + reservas_futuras
    
    for reserva_data in todas_las_reservas:
        servicios_list = reserva_data.pop('servicios', [])
        torneo = reserva_data.pop('torneo', None)
        
        reserva = Reserva.objects.create(**reserva_data)
        
        if servicios_list:
            reserva.servicios.set(servicios_list)
        
        if torneo:
            reserva.torneo = torneo
            reserva.save()
        
        reservas_creadas.append(reserva)
        fecha_str = reserva.fecha_hora_inicio.strftime('%d/%m/%Y %H:%M')
        print(f"  - {reserva.cliente.nombre} {reserva.cliente.apellido} - {reserva.cancha.nombre} - {fecha_str} [{reserva.estado}]")
    
    return reservas_creadas

def crear_pagos(reservas):
    """Crea pagos para las reservas"""
    print("\n7. Creando pagos...")
    
    pagos_creados = []
    
    for reserva in reservas:
        # Calcular monto total
        horas = (reserva.fecha_hora_fin - reserva.fecha_hora_inicio).total_seconds() / 3600
        monto_cancha = float(reserva.cancha.precio_por_hora) * horas
        monto_servicios = sum(float(s.costo_adicional) for s in reserva.servicios.all())
        monto_total = Decimal(str(monto_cancha + monto_servicios))
        
        # Determinar estado y metodo segun estado de reserva y fecha
        if reserva.estado == 'CONFIRMADA':
            estado_pago = 'PAGADO'
            metodo = 'TRANSFERENCIA' if reservas.index(reserva) % 3 == 0 else 'EFECTIVO' if reservas.index(reserva) % 3 == 1 else 'TARJETA_CREDITO'
            fecha_pago = reserva.fecha_creacion
            comprobante = f"COMP-{1000 + reservas.index(reserva)}"
        elif reserva.estado == 'CANCELADA':
            estado_pago = 'REEMBOLSADO'
            metodo = 'TRANSFERENCIA'
            fecha_pago = reserva.fecha_creacion + timedelta(hours=1)
            comprobante = f"REF-{2000 + reservas.index(reserva)}"
        else:  # PENDIENTE
            estado_pago = 'PENDIENTE'
            metodo = None
            fecha_pago = None
            comprobante = None
        
        pago = Pago.objects.create(
            reserva=reserva,
            monto_total=monto_total,
            estado=estado_pago,
            metodo_pago=metodo,
            fecha_pago=fecha_pago,
            comprobante=comprobante
        )
        
        pagos_creados.append(pago)
        print(f"  - Pago para reserva #{reserva.id} - ${monto_total:.2f} [{estado_pago}]")
    
    return pagos_creados

def superpoblar_reservas(clientes, canchas, servicios, torneos, num_reservas=500):
    """
    Crea una gran cantidad de reservas distribuidas a lo largo de 2025
    para simular un uso real del sistema
    """
    print(f"\n7. Creando {num_reservas} reservas adicionales para 2025...")
    print("   (Esto puede tomar un momento...)")
    
    reservas_creadas = []
    estados_posibles = ['CONFIRMADA', 'CONFIRMADA', 'CONFIRMADA', 'PENDIENTE', 'CANCELADA']  # 60% confirmadas
    
    # Horarios de inicio posibles (8:00 a 21:00)
    horas_inicio = list(range(8, 22))
    
    # Duraciones posibles en horas
    duraciones = [1, 2, 3, 4]
    
    # Fecha de inicio: 1 de enero de 2025
    fecha_inicio = datetime(2025, 1, 1)
    fecha_fin = datetime(2025, 12, 31)
    
    # Calcular el rango de días
    dias_totales = (fecha_fin - fecha_inicio).days
    
    intentos = 0
    max_intentos = num_reservas * 5  # Permitir hasta 5x intentos para evitar loops infinitos
    
    while len(reservas_creadas) < num_reservas and intentos < max_intentos:
        intentos += 1
        
        try:
            # Generar fecha aleatoria en 2025
            dias_aleatorios = random.randint(0, dias_totales)
            fecha_reserva = fecha_inicio + timedelta(days=dias_aleatorios)
            
            # Seleccionar hora de inicio aleatoria
            hora_inicio = random.choice(horas_inicio)
            
            # Seleccionar duración aleatoria
            duracion = random.choice(duraciones)
            
            # Calcular hora de fin
            hora_fin = hora_inicio + duracion
            
            # Validar que la hora de fin no exceda las 23:00
            if hora_fin > 23:
                continue
            
            # Crear datetimes timezone-aware
            inicio = timezone.make_aware(datetime(
                fecha_reserva.year, 
                fecha_reserva.month, 
                fecha_reserva.day, 
                hora_inicio, 
                0
            ))
            fin = timezone.make_aware(datetime(
                fecha_reserva.year, 
                fecha_reserva.month, 
                fecha_reserva.day, 
                hora_fin, 
                0
            ))
            
            # Seleccionar cliente y cancha aleatoriamente
            cliente = random.choice(clientes)
            cancha = random.choice(canchas)
            
            # Verificar si hay conflicto (opcional, para más realismo)
            conflicto = Reserva.objects.filter(
                cancha=cancha,
                fecha_hora_inicio__lt=fin,
                fecha_hora_fin__gt=inicio
            ).exclude(estado='CANCELADA').exists()
            
            if conflicto:
                continue  # Saltar esta reserva si hay conflicto
            
            # Seleccionar estado aleatorio
            estado = random.choice(estados_posibles)
            
            # Seleccionar servicios aleatorios (0 a 3 servicios)
            num_servicios = random.randint(0, 3)
            servicios_seleccionados = random.sample(servicios, num_servicios) if num_servicios > 0 else []
            
            # Seleccionar torneo aleatorio (10% de probabilidad)
            torneo = random.choice(torneos) if random.random() < 0.1 and torneos else None
            
            # Crear observaciones aleatorias
            observaciones_posibles = [
                'Reserva regular',
                'Partido amistoso',
                'Entrenamiento',
                'Torneo interno',
                'Cumpleaños',
                'Evento empresarial',
                'Clase de fútbol',
                'Partido competitivo',
                '',
                ''
            ]
            observaciones = random.choice(observaciones_posibles)
            
            # Crear la reserva
            reserva = Reserva.objects.create(
                cliente=cliente,
                cancha=cancha,
                fecha_hora_inicio=inicio,
                fecha_hora_fin=fin,
                estado=estado,
                observaciones=observaciones,
                torneo=torneo
            )
            
            # Agregar servicios
            if servicios_seleccionados:
                reserva.servicios.set(servicios_seleccionados)
            
            reservas_creadas.append(reserva)
            
            # Mostrar progreso cada 50 reservas
            if len(reservas_creadas) % 50 == 0:
                print(f"   Creadas {len(reservas_creadas)}/{num_reservas} reservas...")
        
        except Exception as e:
            # Si hay algún error, continuar con la siguiente
            continue
    
    print(f"   ✓ Creadas {len(reservas_creadas)} reservas exitosamente!")
    
    # Crear pagos para las reservas
    print("\n8. Creando pagos para las reservas adicionales...")
    pagos_creados = 0
    
    for reserva in reservas_creadas:
        if reserva.estado == 'CONFIRMADA':
            # 90% de las confirmadas están pagadas
            estado_pago = 'PAGADO' if random.random() < 0.9 else 'PENDIENTE'
        elif reserva.estado == 'PENDIENTE':
            estado_pago = 'PENDIENTE'
        else:  # CANCELADA
            # 50% de las canceladas tienen reembolso
            estado_pago = 'REEMBOLSADO' if random.random() < 0.5 else 'PAGADO'
        
        monto = reserva.calcular_costo_total()
        
        Pago.objects.create(
            reserva=reserva,
            monto_total=monto,
            estado=estado_pago,
            fecha_pago=reserva.fecha_creacion
        )
        pagos_creados += 1
        
        if pagos_creados % 100 == 0:
            print(f"   Creados {pagos_creados} pagos...")
    
    print(f"   ✓ Creados {pagos_creados} pagos exitosamente!")
    
    return reservas_creadas

def mostrar_resumen():
    """Muestra resumen de datos creados"""
    print("\n" + "="*60)
    print("RESUMEN DE DATOS CREADOS")
    print("="*60)
    print(f"Tipos de Cancha: {TipoCancha.objects.count()}")
    print(f"Clientes: {Cliente.objects.count()}")
    print(f"Canchas: {Cancha.objects.count()}")
    print(f"Servicios: {Servicio.objects.count()}")
    print(f"Torneos: {Torneo.objects.count()}")
    print(f"Reservas: {Reserva.objects.count()}")
    print(f"  - Confirmadas: {Reserva.objects.filter(estado='CONFIRMADA').count()}")
    print(f"  - Pendientes: {Reserva.objects.filter(estado='PENDIENTE').count()}")
    print(f"  - Canceladas: {Reserva.objects.filter(estado='CANCELADA').count()}")
    print(f"Pagos: {Pago.objects.count()}")
    print(f"  - Pagados: {Pago.objects.filter(estado='PAGADO').count()}")
    print(f"  - Pendientes: {Pago.objects.filter(estado='PENDIENTE').count()}")
    print(f"  - Reembolsados: {Pago.objects.filter(estado='REEMBOLSADO').count()}")
    print("="*60)

def main():
    """Funcion principal"""
    print("\n" + "="*60)
    print("SCRIPT DE POBLACION DE BASE DE DATOS")
    print("Sistema de Reservas Deportivas")
    print("="*60)
    
    try:
        respuesta = input("\nEsto eliminara todos los datos existentes. Continuar? (s/n): ")
        if respuesta.lower() != 's':
            print("Operacion cancelada.")
            return
        
        # Preguntar si se desea superpoblación
        superpoblar = input("\n¿Desea crear 500 reservas adicionales para 2025? (s/n): ")
        crear_superpoblacion = superpoblar.lower() == 's'
        
        # Limpiar datos existentes
        limpiar_datos()
        
        # Crear datos base
        tipos_cancha = crear_tipos_cancha()
        clientes = crear_clientes()
        canchas = crear_canchas(tipos_cancha)
        servicios = crear_servicios()
        torneos = crear_torneos()
        reservas = crear_reservas(clientes, canchas, servicios, torneos)
        pagos = crear_pagos(reservas)
        
        # Crear superpoblación si se solicitó
        if crear_superpoblacion:
            reservas_adicionales = superpoblar_reservas(clientes, canchas, servicios, torneos, 500)
        
        # Mostrar resumen
        mostrar_resumen()
        
        print("\nBase de datos poblada exitosamente!")
        
    except Exception as e:
        print(f"\nError al poblar la base de datos: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
