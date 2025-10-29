"""
Configuración de fixtures para pytest.
Fixtures reutilizables en todos los tests.
"""
import pytest
from django.utils import timezone
from datetime import timedelta

from reservas.models import (
    Cliente, TipoCancha, Cancha, Servicio, 
    Torneo, Reserva, Pago, Equipo
)


@pytest.fixture
def cliente():
    """Cliente de prueba"""
    return Cliente.objects.create(
        nombre="Juan",
        apellido="Pérez",
        dni="12345678",
        email="juan@email.com",
        telefono="11-1234-5678"
    )


@pytest.fixture
def cliente_con_dni_invalido():
    """Cliente con DNI inválido para tests de validación"""
    cliente = Cliente(
        nombre="María",
        apellido="García",
        dni="123",  # DNI muy corto
        email="maria@email.com",
        telefono="11-8765-4321"
    )
    return cliente


@pytest.fixture
def tipo_cancha():
    """Tipo de cancha básico"""
    return TipoCancha.objects.create(nombre="Fútbol 5")


@pytest.fixture
def tipo_cancha_futbol_7():
    """Tipo de cancha para fútbol 7"""
    return TipoCancha.objects.create(nombre="Fútbol 7")


@pytest.fixture
def cancha(tipo_cancha):
    """Cancha básica para tests"""
    return Cancha.objects.create(
        nombre="Cancha 1",
        tipo_cancha=tipo_cancha,
        precio_por_hora=1000
    )


@pytest.fixture
def cancha_2(tipo_cancha):
    """Segunda cancha para tests de disponibilidad"""
    return Cancha.objects.create(
        nombre="Cancha 2",
        tipo_cancha=tipo_cancha,
        precio_por_hora=1200
    )


@pytest.fixture
def servicio():
    """Servicio básico (pelotas)"""
    return Servicio.objects.create(
        nombre="Pelotas",
        costo_adicional=500
    )


@pytest.fixture
def servicio_iluminacion():
    """Servicio de iluminación"""
    return Servicio.objects.create(
        nombre="Iluminación",
        costo_adicional=800
    )


@pytest.fixture
def torneo():
    """Torneo básico para tests"""
    return Torneo.objects.create(
        nombre="Copa Verano 2025",
        fecha_inicio=timezone.now().date() + timedelta(days=7),
        fecha_fin=timezone.now().date() + timedelta(days=14),
        premio="$50,000",
        estado="INSCRIPCION",
        costo_inscripcion=5000,
        descripcion="Torneo de verano"
    )


@pytest.fixture
def reserva_futura(cliente, cancha):
    """Reserva en el futuro con estado PENDIENTE"""
    inicio = timezone.now() + timedelta(days=1, hours=10)
    fin = inicio + timedelta(hours=2)
    
    return Reserva.objects.create(
        cliente=cliente,
        cancha=cancha,
        fecha_hora_inicio=inicio,
        fecha_hora_fin=fin,
        estado='PENDIENTE'
    )


@pytest.fixture
def reserva_con_servicios(reserva_futura, servicio, servicio_iluminacion):
    """Reserva con servicios adicionales"""
    reserva_futura.servicios.add(servicio, servicio_iluminacion)
    return reserva_futura


@pytest.fixture
def pago_pendiente(reserva_futura):
    """Pago en estado PENDIENTE"""
    return Pago.objects.create(
        reserva=reserva_futura,
        monto_total=2000,
        estado='PENDIENTE'
    )


@pytest.fixture
def pago_pagado(reserva_futura):
    """Pago ya realizado"""
    return Pago.objects.create(
        reserva=reserva_futura,
        monto_total=2000,
        estado='PAGADO',
        fecha_pago=timezone.now(),
        metodo_pago='EFECTIVO',
        comprobante='COMP-001'
    )


@pytest.fixture
def equipos_torneo(torneo):
    """4 equipos inscritos en un torneo"""
    equipos = []
    for i in range(4):
        equipo = Equipo.objects.create(nombre=f"Equipo {i+1}")
        torneo.equipos.add(equipo)
        equipos.append(equipo)
    return equipos


@pytest.fixture
def fecha_futura():
    """Fecha en el futuro para tests"""
    return timezone.now() + timedelta(days=1, hours=10)


@pytest.fixture
def fecha_pasada():
    """Fecha en el pasado para tests de validación"""
    return timezone.now() - timedelta(days=1, hours=10)
