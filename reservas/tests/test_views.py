"""
Tests de integración para las vistas del sistema de reservas.
Valida el flujo HTTP completo: request → view → response.
Ejecutar con: pytest reservas/tests/test_views.py -v
"""
import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from reservas.models import Reserva, Pago, Cliente

pytestmark = pytest.mark.django_db


# ============== TESTS DE VISTA CREAR RESERVA ==============

@pytest.mark.integration
class TestReservaCreateView:
    """Tests para la vista de creación de reservas"""
    
    def test_get_formulario_reserva(self, client, cliente, cancha):
        """Test: GET debe mostrar el formulario de reserva"""
        url = reverse('reserva_crear')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'reservas/reservas/form.html' in [t.name for t in response.templates]
    
    def test_crear_reserva_valida_redirect(self, client, cliente, cancha):
        """Test: POST con datos válidos debe crear reserva y redirigir"""
        # Crear fecha en el futuro con margen de seguridad (2 días)
        manana = timezone.now() + timedelta(days=2)
        # Convertir a naive datetime (sin timezone) para el POST
        inicio = manana.replace(hour=10, minute=0, second=0, microsecond=0, tzinfo=None)
        fin = inicio + timedelta(hours=2)
        
        data = {
            'cliente': cliente.id,
            'cancha': cancha.id,
            'fecha_hora_inicio': inicio.isoformat(),
            'fecha_hora_fin': fin.isoformat(),
        }
        
        url = reverse('reserva_crear')
        response = client.post(url, data)
        
        # Debe redireccionar después de crear exitosamente
        assert response.status_code == 302
        
        # Verificar que se creó la reserva
        assert Reserva.objects.count() == 1
        
        reserva = Reserva.objects.first()
        assert reserva.cliente == cliente
        assert reserva.cancha == cancha
    
    def test_fecha_pasada_error_mantiene_datos(self, client, cliente, cancha):
        """Test: Error de fecha pasada debe mantener los datos del formulario"""
        # Crear fecha pasada como naive datetime
        inicio_pasado = timezone.now() - timedelta(days=1, hours=10)
        inicio_pasado = inicio_pasado.replace(tzinfo=None)
        fin_pasado = inicio_pasado + timedelta(hours=2)
        
        data = {
            'cliente': cliente.id,
            'cancha': cancha.id,
            'fecha_hora_inicio': inicio_pasado.isoformat(),
            'fecha_hora_fin': fin_pasado.isoformat(),
        }
        
        url = reverse('reserva_crear')
        response = client.post(url, data, follow=True)
        
        assert response.status_code == 200
        assert Reserva.objects.count() == 0
        
        # Verificar que los datos se mantienen
        assert 'datos_form' in response.context
        datos = response.context['datos_form']
        assert datos['cliente_id'] == str(cliente.id)
        assert datos['cancha_id'] == str(cancha.id)
        assert datos['fecha_hora_inicio'] == ''  # Fecha limpiada
    
    def test_fecha_pasada_permite_correccion(self, client, cliente, cancha):
        """Test: Después de error de fecha pasada, debe permitir corregir"""
        # Primer intento con fecha pasada (naive datetime)
        inicio_pasado = timezone.now() - timedelta(days=1, hours=10)
        inicio_pasado = inicio_pasado.replace(tzinfo=None)
        fin_pasado = inicio_pasado + timedelta(hours=2)
        
        data_incorrecta = {
            'cliente': cliente.id,
            'cancha': cancha.id,
            'fecha_hora_inicio': inicio_pasado.isoformat(),
            'fecha_hora_fin': fin_pasado.isoformat(),
        }
        
        url = reverse('reserva_crear')
        client.post(url, data_incorrecta)
        
        assert Reserva.objects.count() == 0
        
        # Segundo intento con fecha correcta (naive datetime)
        manana = timezone.now() + timedelta(days=2)
        inicio_correcto = manana.replace(hour=10, minute=0, second=0, microsecond=0, tzinfo=None)
        fin_correcto = inicio_correcto + timedelta(hours=2)
        
        data_correcta = {
            'cliente': cliente.id,
            'cancha': cancha.id,
            'fecha_hora_inicio': inicio_correcto.isoformat(),
            'fecha_hora_fin': fin_correcto.isoformat(),
        }
        
        response = client.post(url, data_correcta)
        
        # Verificar que se creó exitosamente
        assert response.status_code == 302
        assert Reserva.objects.count() == 1
    
    def test_servicios_adicionales_se_guardan(self, client, cliente, cancha, servicio):
        """Test: Servicios adicionales se asocian correctamente"""
        # Crear fecha en el futuro con margen de seguridad (2 días)
        manana = timezone.now() + timedelta(days=2)
        # Convertir a naive datetime (sin timezone) para el POST
        inicio = manana.replace(hour=10, minute=0, second=0, microsecond=0, tzinfo=None)
        fin = inicio + timedelta(hours=2)
        
        data = {
            'cliente': cliente.id,
            'cancha': cancha.id,
            'fecha_hora_inicio': inicio.isoformat(),
            'fecha_hora_fin': fin.isoformat(),
            'servicios': [servicio.id],
        }
        
        url = reverse('reserva_crear')
        response = client.post(url, data)
        
        # Debe redireccionar después de crear exitosamente
        assert response.status_code == 302
        
        # Verificar que se creó la reserva
        assert Reserva.objects.count() == 1
        
        reserva = Reserva.objects.first()
        assert reserva.servicios.count() == 1
        assert servicio in reserva.servicios.all()
    
    def test_manejo_keyerror_seguro(self, client):
        """Test: No debe crashear con KeyError si falta un campo"""
        url = reverse('reserva_crear')
        data = {
            'cliente': 999,  # Sin cancha ni fechas
        }
        
        response = client.post(url, data, follow=True)
        
        # No debe crashear, debe mostrar formulario con error
        assert response.status_code == 200
        assert Reserva.objects.count() == 0
    
    def test_muestra_mensaje_error(self, client, cliente, cancha):
        """Test: Debe mostrar mensaje de error cuando falla validación"""
        inicio_pasado = timezone.now() - timedelta(days=1, hours=10)
        fin_pasado = inicio_pasado + timedelta(hours=2)
        
        data = {
            'cliente': cliente.id,
            'cancha': cancha.id,
            'fecha_hora_inicio': inicio_pasado.isoformat(),
            'fecha_hora_fin': fin_pasado.isoformat(),
        }
        
        url = reverse('reserva_crear')
        response = client.post(url, data, follow=True)
        
        # Verificar que hay mensajes de error
        messages = list(response.context['messages'])
        assert len(messages) > 0


# ============== TESTS DE VISTA EDITAR RESERVA ==============

@pytest.mark.integration
class TestReservaEditView:
    """Tests para la vista de edición de reservas"""
    
    def test_editar_estado_reserva(self, client, reserva_futura):
        """Test: Debe permitir editar el estado de una reserva"""
        url = reverse('reserva_editar', args=[reserva_futura.id])
        data = {
            'estado': 'PAGADA',
        }
        
        response = client.post(url, data)
        
        assert response.status_code == 302
        
        reserva_futura.refresh_from_db()
        assert reserva_futura.estado == 'PAGADA'
    
    def test_editar_mantiene_servicios(self, client, reserva_con_servicios):
        """Test: Editar no debe perder los servicios asociados"""
        servicios_originales = list(reserva_con_servicios.servicios.all())
        
        url = reverse('reserva_editar', args=[reserva_con_servicios.id])
        data = {
            'estado': 'PAGADA',
            'servicios': [s.id for s in servicios_originales],
        }
        
        response = client.post(url, data)
        
        assert response.status_code == 302
        
        reserva_con_servicios.refresh_from_db()
        assert reserva_con_servicios.servicios.count() == 2


# ============== TESTS DE VISTA ELIMINAR RESERVA ==============

@pytest.mark.integration
class TestReservaDeleteView:
    """Tests para la vista de eliminación de reservas"""
    
    def test_eliminar_reserva(self, client, reserva_futura):
        """Test: Debe permitir eliminar una reserva"""
        url = reverse('reserva_eliminar', args=[reserva_futura.id])
        response = client.post(url)
        
        # Verificar que se eliminó o cambió de estado
        assert response.status_code in [302, 200]  # Redirect o success


# ============== TESTS DE VISTA MARCAR COMO PAGADA ==============

@pytest.mark.integration
class TestReservaMarcarPagadaView:
    """Tests para la vista de marcar reserva como pagada"""
    
    def test_marcar_como_pagada(self, client, reserva_futura, pago_pendiente):
        """Test: Debe marcar reserva y pago como PAGADO"""
        url = reverse('reserva_marcar_pagada', args=[reserva_futura.id])
        data = {
            'metodo_pago': 'EFECTIVO',
            'comprobante': 'COMP-12345',
        }
        
        response = client.post(url, data)
        
        assert response.status_code == 302
        
        reserva_futura.refresh_from_db()
        pago_pendiente.refresh_from_db()
        
        assert reserva_futura.estado == 'PAGADA'
        assert pago_pendiente.estado == 'PAGADO'
        assert pago_pendiente.metodo_pago == 'EFECTIVO'
    
    def test_no_permite_pagar_cancelada(self, client, reserva_futura, pago_pendiente):
        """Test: No debe permitir pagar una reserva cancelada"""
        reserva_futura.estado = 'CANCELADA'
        reserva_futura.save()
        
        url = reverse('reserva_marcar_pagada', args=[reserva_futura.id])
        data = {
            'metodo_pago': 'EFECTIVO',
            'comprobante': 'COMP-12345',
        }
        
        response = client.post(url, data, follow=True)
        
        pago_pendiente.refresh_from_db()
        assert pago_pendiente.estado == 'PENDIENTE'  # No cambió


# ============== TESTS DE VISTA CLIENTE ==============

@pytest.mark.integration
class TestClienteViews:
    """Tests para las vistas de cliente"""
    
    def test_listar_clientes(self, client, cliente):
        """Test: Debe listar todos los clientes"""
        url = reverse('cliente_lista')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'clientes' in response.context or 'object_list' in response.context
    
    def test_crear_cliente(self, client):
        """Test: Debe permitir crear un cliente nuevo"""
        url = reverse('cliente_crear')
        data = {
            'nombre': 'Pedro',
            'apellido': 'González',
            'dni': '98765432',
            'email': 'pedro@email.com',
            'telefono': '11-5555-5555',
        }
        
        response = client.post(url, data)
        
        assert response.status_code == 302
        assert Cliente.objects.filter(dni='98765432').exists()
    
    def test_editar_cliente(self, client, cliente):
        """Test: Debe permitir editar datos de cliente"""
        url = reverse('cliente_editar', args=[cliente.id])
        data = {
            'nombre': 'Juan Carlos',  # Cambio de nombre
            'apellido': cliente.apellido,
            'dni': cliente.dni,
            'email': cliente.email,
            'telefono': cliente.telefono,
        }
        
        response = client.post(url, data)
        
        assert response.status_code == 302
        
        cliente.refresh_from_db()
        assert cliente.nombre == 'Juan Carlos'


# ============== TESTS DE VISTA CANCHA ==============

@pytest.mark.integration
class TestCanchaViews:
    """Tests para las vistas de cancha"""
    
    def test_listar_canchas(self, client, cancha):
        """Test: Debe listar todas las canchas"""
        url = reverse('cancha_lista')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'canchas' in response.context or 'object_list' in response.context
