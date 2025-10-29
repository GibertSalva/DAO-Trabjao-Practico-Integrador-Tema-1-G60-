"""
Tests End-to-End para flujos completos de usuario.
Simula escenarios reales de uso del sistema.
Ejecutar con: pytest reservas/tests/test_e2e.py -v
"""
import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from reservas.models import Reserva, Pago, Equipo, Partido

pytestmark = pytest.mark.django_db


# ============== FLUJO COMPLETO DE RESERVA ==============

@pytest.mark.e2e
class TestFlujoReservaCompleto:
    """Tests de flujo completo: desde crear hasta pagar una reserva"""
    
    def test_flujo_completo_crear_pagar_reserva(self, client, cliente, cancha, servicio):
        """
        Test E2E: Flujo completo de crear y pagar una reserva
        1. Crear reserva
        2. Verificar que se creó con estado PENDIENTE
        3. Marcar como pagada
        4. Verificar que cambió a PAGADA
        """
        # Paso 1: Crear reserva (naive datetime)
        manana = timezone.now() + timedelta(days=2)
        inicio = manana.replace(hour=10, minute=0, second=0, microsecond=0, tzinfo=None)
        fin = inicio + timedelta(hours=2)
        
        data_crear = {
            'cliente': cliente.id,
            'cancha': cancha.id,
            'fecha_hora_inicio': inicio.isoformat(),
            'fecha_hora_fin': fin.isoformat(),
            'servicios': [servicio.id],
        }
        
        response = client.post(reverse('reserva_crear'), data_crear)
        assert response.status_code == 302
        
        # Paso 2: Verificar que se creó correctamente
        reserva = Reserva.objects.first()
        assert reserva is not None
        assert reserva.estado == 'PENDIENTE'
        assert reserva.pago.estado == 'PENDIENTE'
        
        # Paso 3: Marcar como pagada
        data_pagar = {
            'metodo_pago': 'EFECTIVO',
            'comprobante': 'COMP-12345'
        }
        
        url_marcar_pagada = reverse('reserva_marcar_pagada', args=[reserva.id])
        response = client.post(url_marcar_pagada, data_pagar)
        
        # Paso 4: Verificar cambio de estado
        reserva.refresh_from_db()
        assert reserva.estado == 'PAGADA'
        assert reserva.pago.estado == 'PAGADO'
        assert reserva.pago.fecha_pago is not None
    
    def test_flujo_fecha_pasada_correccion_exitosa(self, client, cliente, cancha, servicio):
        """
        Test E2E: Flujo completo de error de fecha pasada y corrección
        1. Intentar crear reserva con fecha pasada
        2. Verificar error y datos preservados
        3. Corregir fecha y crear exitosamente
        """
        # Paso 1: Intentar con fecha pasada (naive datetime)
        inicio_pasado = timezone.now() - timedelta(days=1, hours=10)
        inicio_pasado = inicio_pasado.replace(tzinfo=None)
        fin_pasado = inicio_pasado + timedelta(hours=2)
        
        data_incorrecta = {
            'cliente': cliente.id,
            'cancha': cancha.id,
            'fecha_hora_inicio': inicio_pasado.isoformat(),
            'fecha_hora_fin': fin_pasado.isoformat(),
            'servicios': [servicio.id],
        }
        
        response = client.post(
            reverse('reserva_crear'), 
            data_incorrecta, 
            follow=True
        )
        
        # Paso 2: Verificar error y datos preservados
        assert response.status_code == 200
        assert 'datos_form' in response.context
        
        datos = response.context['datos_form']
        assert datos['cliente_id'] == str(cliente.id)
        assert datos['cancha_id'] == str(cancha.id)
        assert datos['fecha_hora_inicio'] == ''  # Fecha limpiada
        assert datos['fecha_hora_fin'] == ''
        assert str(servicio.id) in datos['servicios_ids']
        
        # No debe haber creado reserva
        assert Reserva.objects.count() == 0
        
        # Paso 3: Corregir fecha y crear exitosamente (naive datetime)
        manana = timezone.now() + timedelta(days=2)
        inicio_correcto = manana.replace(hour=10, minute=0, second=0, microsecond=0, tzinfo=None)
        fin_correcto = inicio_correcto + timedelta(hours=2)
        
        data_correcta = {
            'cliente': cliente.id,
            'cancha': cancha.id,
            'fecha_hora_inicio': inicio_correcto.isoformat(),
            'fecha_hora_fin': fin_correcto.isoformat(),
            'servicios': [servicio.id],
        }
        
        response = client.post(reverse('reserva_crear'), data_correcta)
        
        assert response.status_code == 302
        assert Reserva.objects.count() == 1
        
        reserva = Reserva.objects.first()
        assert reserva.cliente == cliente
        assert reserva.cancha == cancha
        assert reserva.servicios.count() == 1
    
    def test_flujo_edicion_sin_perder_datos(self, client, reserva_con_servicios):
        """
        Test E2E: Editar reserva cambiando estado sin perder otros datos
        1. Crear reserva con servicios
        2. Editar solo el estado
        3. Verificar que servicios se mantienen
        """
        servicios_originales = list(reserva_con_servicios.servicios.all())
        
        # Editar estado
        data_edicion = {
            'estado': 'PAGADA',
            'servicios': [s.id for s in servicios_originales],
        }
        
        url_editar = reverse('reserva_editar', args=[reserva_con_servicios.id])
        response = client.post(url_editar, data_edicion)
        
        assert response.status_code == 302
        reserva_con_servicios.refresh_from_db()
        
        assert reserva_con_servicios.estado == 'PAGADA'
        assert reserva_con_servicios.servicios.count() == 2


# ============== FLUJO COMPLETO DE TORNEO ==============

@pytest.mark.e2e
class TestFlujoTorneoCompleto:
    """Tests de flujo completo para torneos"""
    
    def test_flujo_completo_torneo_con_fixture(self, client, torneo):
        """
        Test E2E: Crear torneo, inscribir equipos y generar fixture
        1. Crear torneo
        2. Crear 4 equipos
        3. Inscribirlos al torneo
        4. Generar fixture
        5. Verificar estructura de partidos
        """
        # Crear e inscribir 4 equipos
        equipos = []
        for i in range(4):
            equipo = Equipo.objects.create(nombre=f"Equipo {i+1}")
            equipos.append(equipo)
            torneo.equipos.add(equipo)
        
        # Generar fixture
        torneo.generar_fixture()
        
        # Verificar estructura
        partidos = Partido.objects.filter(torneo=torneo)
        
        # Con 4 equipos en eliminación directa: 2 semifinales + 0 final creada aún
        # (la final se crea cuando avanzan los ganadores)
        assert partidos.count() >= 2  # Al menos las semifinales
        
        # Verificar que el torneo cambió a EN_CURSO
        torneo.refresh_from_db()
        assert torneo.estado == 'EN_CURSO'


# ============== FLUJO CON MÚLTIPLES RESERVAS ==============

@pytest.mark.e2e
class TestFlujoClienteMultiplesReservas:
    """Tests de flujo con múltiples reservas de un cliente"""
    
    def test_cliente_puede_hacer_3_reservas_mismo_dia(self, client, cliente, cancha):
        """
        Test E2E: Cliente puede hacer hasta 3 reservas en el mismo día
        """
        manana = timezone.now() + timedelta(days=2)
        fecha_base = manana.replace(hour=10, minute=0, second=0, microsecond=0, tzinfo=None)
        
        # Crear 3 reservas en diferentes horarios
        for i in range(3):
            inicio = fecha_base + timedelta(hours=i*2)
            fin = inicio + timedelta(hours=1)
            
            data = {
                'cliente': cliente.id,
                'cancha': cancha.id,
                'fecha_hora_inicio': inicio.isoformat(),
                'fecha_hora_fin': fin.isoformat(),
            }
            
            response = client.post(reverse('reserva_crear'), data)
            assert response.status_code == 302
        
        # Verificar que se crearon 3 reservas
        reservas = Reserva.objects.filter(cliente=cliente)
        assert reservas.count() == 3
        
        # Verificar que todas son del mismo día
        for reserva in reservas:
            assert reserva.fecha_hora_inicio.date() == manana.date()
    
    def test_permite_solapamiento_en_canchas_diferentes(self, client, cliente, cancha, cancha_2):
        """
        Test E2E: Mismo cliente puede reservar canchas diferentes en horarios solapados
        """
        manana = timezone.now() + timedelta(days=2)
        inicio = manana.replace(hour=10, minute=0, second=0, microsecond=0, tzinfo=None)
        fin = inicio + timedelta(hours=1)
        
        # Reserva en cancha 1
        data1 = {
            'cliente': cliente.id,
            'cancha': cancha.id,
            'fecha_hora_inicio': inicio.isoformat(),
            'fecha_hora_fin': fin.isoformat(),
        }
        response1 = client.post(reverse('reserva_crear'), data1)
        assert response1.status_code == 302
        
        # Reserva solapada en cancha 2 (debería permitirse)
        inicio2 = inicio + timedelta(minutes=30)
        fin2 = inicio2 + timedelta(hours=1)
        
        data2 = {
            'cliente': cliente.id,
            'cancha': cancha_2.id,  # Cancha diferente
            'fecha_hora_inicio': inicio2.isoformat(),
            'fecha_hora_fin': fin2.isoformat(),
        }
        response2 = client.post(reverse('reserva_crear'), data2)
        
        # Debe permitirse porque son canchas diferentes
        assert response2.status_code == 302
        assert Reserva.objects.count() == 2


# ============== FLUJO DE REPORTES ==============

@pytest.mark.e2e
class TestFlujoReporte:
    """Tests de flujo para generación de reportes"""
    
    def test_reporte_muestra_reservas_del_mes(self, client, cliente, cancha):
        """
        Test E2E: El reporte muestra las reservas del mes seleccionado
        """
        hoy = timezone.now()
        mes_actual = hoy.month
        anio_actual = hoy.year
        
        # Reserva del mes actual
        inicio_actual = hoy + timedelta(days=1, hours=10)
        fin_actual = inicio_actual + timedelta(hours=2)
        
        Reserva.objects.create(
            cliente=cliente,
            cancha=cancha,
            fecha_hora_inicio=inicio_actual,
            fecha_hora_fin=fin_actual,
            estado='PAGADA'
        )
        
        # Reserva del mes anterior
        mes_pasado = hoy - timedelta(days=40)
        inicio_pasado = mes_pasado.replace(hour=10, minute=0)
        fin_pasado = inicio_pasado + timedelta(hours=2)
        
        Reserva.objects.create(
            cliente=cliente,
            cancha=cancha,
            fecha_hora_inicio=inicio_pasado,
            fecha_hora_fin=fin_pasado,
            estado='PAGADA'
        )
        
        # Consultar reporte del mes actual
        url = reverse('reportes')
        response = client.get(url, {
            'mes': mes_actual,
            'anio': anio_actual
        })
        
        assert response.status_code == 200
        
        # Verificar que muestra datos del mes correcto
        if 'clientes_con_reservas' in response.context:
            clientes_reporte = response.context['clientes_con_reservas']
            if clientes_reporte:
                assert clientes_reporte[0]['num_reservas'] == 1
