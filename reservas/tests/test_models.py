"""
Tests unitarios para los modelos del sistema de reservas.
Valida la lógica de negocio y las restricciones de datos.
Ejecutar con: pytest reservas/tests/test_models.py -v
"""
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from reservas.models import (
    Cliente, TipoCancha, Cancha, Servicio, 
    Torneo, Reserva, Pago
)

pytestmark = pytest.mark.django_db


# ============== TESTS DE CLIENTE ==============

@pytest.mark.unit
class TestCliente:
    """Tests para el modelo Cliente"""
    
    def test_crear_cliente_valido(self, cliente):
        """Test: Se puede crear un cliente con datos válidos"""
        assert cliente.nombre == "Juan"
        assert cliente.apellido == "Pérez"
        assert str(cliente) == "Juan Pérez"
    
    def test_validacion_dni_duplicado(self, cliente):
        """Test: No permite DNI duplicado"""
        with pytest.raises(Exception):  # IntegrityError
            Cliente.objects.create(
                nombre="María",
                apellido="García",
                dni="12345678",  # DNI duplicado
                email="maria@email.com",
                telefono="11-9999-9999"
            )
    
    def test_validacion_dni_todo_ceros(self):
        """Test: No permite DNI con todos ceros"""
        cliente = Cliente(
            nombre="Test",
            apellido="User",
            dni="00000000",
            email="test@email.com",
            telefono="11-0000-0000"
        )
        with pytest.raises(ValidationError) as exc_info:
            cliente.clean()
        
        assert 'dni' in str(exc_info.value).lower()
    
    def test_validacion_dni_muy_corto(self, cliente_con_dni_invalido):
        """Test: No permite DNI muy corto"""
        with pytest.raises(ValidationError) as exc_info:
            cliente_con_dni_invalido.full_clean()  # full_clean valida los validators
        
        assert 'dni' in str(exc_info.value).lower()
    
    def test_email_debe_ser_valido(self):
        """Test: Email debe tener formato válido"""
        cliente = Cliente(
            nombre="Test",
            apellido="User",
            dni="87654321",
            email="email_invalido",  # Sin @
            telefono="11-0000-0000"
        )
        with pytest.raises(ValidationError):
            cliente.full_clean()
    
    def test_str_representacion(self, cliente):
        """Test: __str__ retorna nombre completo"""
        assert str(cliente) == "Juan Pérez"


# ============== TESTS DE CANCHA ==============

@pytest.mark.unit
class TestCancha:
    """Tests para el modelo Cancha"""
    
    def test_crear_cancha_valida(self, cancha, tipo_cancha):
        """Test: Se puede crear una cancha con datos válidos"""
        assert cancha.nombre == "Cancha 1"
        assert cancha.tipo_cancha == tipo_cancha
        assert cancha.precio_por_hora == 1000
    
    def test_precio_debe_ser_positivo(self, tipo_cancha):
        """Test: Precio por hora debe ser positivo"""
        cancha = Cancha(
            nombre="Cancha Test",
            tipo_cancha=tipo_cancha,
            precio_por_hora=-100  # Negativo
        )
        with pytest.raises(ValidationError) as exc_info:
            cancha.clean()
        
        assert 'precio' in str(exc_info.value).lower()
    
    def test_precio_debe_ser_mayor_a_cero(self, tipo_cancha):
        """Test: Precio por hora debe ser mayor a 0"""
        cancha = Cancha(
            nombre="Cancha Test",
            tipo_cancha=tipo_cancha,
            precio_por_hora=0
        )
        with pytest.raises(ValidationError):
            cancha.full_clean()  # full_clean valida los validators (MinValueValidator)
    
    def test_str_representacion(self, cancha):
        """Test: __str__ retorna nombre y tipo"""
        assert "Cancha 1" in str(cancha)
        assert "Fútbol 5" in str(cancha)


# ============== TESTS DE RESERVA ==============

@pytest.mark.unit
class TestReserva:
    """Tests para el modelo Reserva (lógica de negocio principal)"""
    
    def test_crear_reserva_valida(self, reserva_futura):
        """Test: Se puede crear una reserva con datos válidos"""
        assert reserva_futura.estado == 'PENDIENTE'
        assert reserva_futura.cliente is not None
        assert reserva_futura.cancha is not None
    
    def test_no_permite_reservar_en_pasado(self, cliente, cancha):
        """Test: No permite crear reserva con fecha pasada"""
        inicio_pasado = timezone.now() - timedelta(days=1, hours=10)
        fin_pasado = inicio_pasado + timedelta(hours=2)
        
        reserva = Reserva(
            cliente=cliente,
            cancha=cancha,
            fecha_hora_inicio=inicio_pasado,
            fecha_hora_fin=fin_pasado
        )
        
        with pytest.raises(ValidationError) as exc_info:
            reserva.clean()
        
        error_msg = str(exc_info.value).lower()
        assert 'pasado' in error_msg or 'anterior' in error_msg
    
    def test_fecha_fin_debe_ser_posterior_a_inicio(self, cliente, cancha):
        """Test: Fecha fin debe ser posterior a fecha inicio"""
        inicio = timezone.now() + timedelta(days=1, hours=10)
        fin = inicio - timedelta(hours=1)  # Fin antes del inicio
        
        reserva = Reserva(
            cliente=cliente,
            cancha=cancha,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=fin
        )
        
        with pytest.raises(ValidationError) as exc_info:
            reserva.clean()
        
        assert 'posterior' in str(exc_info.value).lower()
    
    def test_duracion_minima_1_hora(self, cliente, cancha):
        """Test: Duración mínima de 1 hora"""
        inicio = timezone.now() + timedelta(days=1, hours=10)
        fin = inicio + timedelta(minutes=30)  # Solo 30 minutos
        
        reserva = Reserva(
            cliente=cliente,
            cancha=cancha,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=fin
        )
        
        with pytest.raises(ValidationError) as exc_info:
            reserva.clean()
        
        assert 'hora' in str(exc_info.value).lower()
    
    def test_duracion_maxima_4_horas(self, cliente, cancha):
        """Test: Duración máxima de 4 horas"""
        # Usar hora válida (entre 8 AM y 11 PM)
        manana = timezone.now() + timedelta(days=1)
        inicio = manana.replace(hour=10, minute=0, second=0, microsecond=0)
        fin = inicio + timedelta(hours=5)  # 5 horas
        
        reserva = Reserva(
            cliente=cliente,
            cancha=cancha,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=fin
        )
        
        with pytest.raises(ValidationError) as exc_info:
            reserva.clean()
        
        assert '4' in str(exc_info.value)
    
    def test_horario_permitido_8am_a_11pm(self, cliente, cancha):
        """Test: Horario permitido de 8 AM a 11 PM"""
        # Reserva a las 7 AM (antes del horario)
        manana = timezone.now() + timedelta(days=1)
        inicio = manana.replace(hour=7, minute=0, second=0, microsecond=0)
        fin = inicio + timedelta(hours=1)
        
        reserva = Reserva(
            cliente=cliente,
            cancha=cancha,
            fecha_hora_inicio=inicio,
            fecha_hora_fin=fin
        )
        
        with pytest.raises(ValidationError) as exc_info:
            reserva.clean()
        
        # El mensaje de error dice "El complejo abre a las 08:00"
        assert 'abre' in str(exc_info.value).lower() or '08:00' in str(exc_info.value)
    
    def test_no_permite_solapamiento_misma_cancha(self, reserva_futura, cliente):
        """Test: No permite solapamiento en la misma cancha"""
        # Intentar crear reserva solapada con horario válido
        manana = timezone.now() + timedelta(days=1)
        inicio_solapado = manana.replace(hour=10, minute=30, second=0, microsecond=0)
        fin_solapado = inicio_solapado + timedelta(hours=1)
        
        # Crear una reserva existente primero
        reserva_existente = Reserva.objects.create(
            cliente=cliente,
            cancha=reserva_futura.cancha,
            fecha_hora_inicio=manana.replace(hour=10, minute=0, second=0, microsecond=0),
            fecha_hora_fin=manana.replace(hour=12, minute=0, second=0, microsecond=0)
        )
        
        # Intentar crear reserva solapada
        reserva_solapada = Reserva(
            cliente=cliente,
            cancha=reserva_futura.cancha,  # Misma cancha
            fecha_hora_inicio=inicio_solapado,
            fecha_hora_fin=fin_solapado
        )
        
        with pytest.raises(ValidationError) as exc_info:
            reserva_solapada.clean()
        
        error_msg = str(exc_info.value).lower()
        assert 'disponible' in error_msg or 'cancha' in error_msg
    
    def test_permite_reservas_consecutivas_misma_cancha(self, reserva_futura, cliente):
        """Test: Permite reservas consecutivas sin solapamiento"""
        # Reserva inmediatamente después
        inicio_siguiente = reserva_futura.fecha_hora_fin
        fin_siguiente = inicio_siguiente + timedelta(hours=1)
        
        reserva_siguiente = Reserva(
            cliente=cliente,
            cancha=reserva_futura.cancha,
            fecha_hora_inicio=inicio_siguiente,
            fecha_hora_fin=fin_siguiente
        )
        
        # No debe lanzar excepción
        reserva_siguiente.clean()
        reserva_siguiente.save()
        
        assert Reserva.objects.count() == 2
    
    def test_maximo_3_reservas_por_dia_cliente(self, cliente, cancha):
        """Test: Máximo 3 reservas por día por cliente"""
        manana = timezone.now() + timedelta(days=1)
        fecha_base = manana.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Crear 3 reservas en el mismo día
        for i in range(3):
            inicio = fecha_base + timedelta(hours=i * 2)
            fin = inicio + timedelta(hours=1)
            
            Reserva.objects.create(
                cliente=cliente,
                cancha=cancha,
                fecha_hora_inicio=inicio,
                fecha_hora_fin=fin
            )
        
        # Intentar crear la cuarta
        inicio_cuarta = fecha_base + timedelta(hours=6)
        fin_cuarta = inicio_cuarta + timedelta(hours=1)
        
        reserva_cuarta = Reserva(
            cliente=cliente,
            cancha=cancha,
            fecha_hora_inicio=inicio_cuarta,
            fecha_hora_fin=fin_cuarta
        )
        
        with pytest.raises(ValidationError) as exc_info:
            reserva_cuarta.clean()
        
        assert '3' in str(exc_info.value)
    
    def test_calcular_costo_total_solo_cancha(self, reserva_futura):
        """Test: Calcular costo total sin servicios adicionales"""
        # 2 horas * 1000 por hora = 2000
        costo = reserva_futura.calcular_costo_total()
        assert costo == Decimal('2000.00')
    
    def test_calcular_costo_total_con_servicios(self, reserva_con_servicios):
        """Test: Calcular costo total con servicios adicionales"""
        # 2 horas * 1000 + 500 (pelotas) + 800 (iluminación) = 3300
        costo = reserva_con_servicios.calcular_costo_total()
        assert costo == Decimal('3300.00')
    
    def test_fecha_usa_timezone_aware(self, reserva_futura):
        """Test: Fechas deben ser timezone-aware"""
        assert reserva_futura.fecha_hora_inicio.tzinfo is not None
        assert reserva_futura.fecha_hora_fin.tzinfo is not None
    
    def test_str_representacion(self, reserva_futura):
        """Test: __str__ muestra info relevante"""
        str_repr = str(reserva_futura)
        assert reserva_futura.cliente.nombre in str_repr
        assert reserva_futura.cancha.nombre in str_repr


# ============== TESTS DE PAGO ==============

@pytest.mark.unit
class TestPago:
    """Tests para el modelo Pago"""
    
    def test_crear_pago_pendiente(self, pago_pendiente):
        """Test: Se puede crear un pago pendiente"""
        assert pago_pendiente.estado == 'PENDIENTE'
        assert pago_pendiente.fecha_pago is None
    
    def test_marcar_como_pagado(self, pago_pendiente):
        """Test: Marcar pago como pagado actualiza estado y fecha"""
        pago_pendiente.marcar_como_pagado('EFECTIVO', 'COMP-123')
        
        assert pago_pendiente.estado == 'PAGADO'
        assert pago_pendiente.fecha_pago is not None
        assert pago_pendiente.metodo_pago == 'EFECTIVO'
        assert pago_pendiente.comprobante == 'COMP-123'
    
    def test_monto_debe_ser_positivo(self, reserva_futura):
        """Test: Monto total debe ser positivo"""
        pago = Pago(
            reserva=reserva_futura,
            monto_total=Decimal('-100.00'),  # Negativo
            estado='PENDIENTE'
        )
        
        with pytest.raises(ValidationError) as exc_info:
            pago.clean()
        
        assert 'monto' in str(exc_info.value).lower()


# ============== TESTS DE TORNEO ==============

@pytest.mark.unit
class TestTorneo:
    """Tests para el modelo Torneo"""
    
    def test_crear_torneo_valido(self, torneo):
        """Test: Se puede crear un torneo con datos válidos"""
        assert torneo.nombre == "Copa Verano 2025"
        assert torneo.estado == "INSCRIPCION"
        assert torneo.costo_inscripcion == 5000
    
    def test_fecha_fin_debe_ser_posterior_a_inicio(self):
        """Test: Fecha fin debe ser posterior a fecha inicio"""
        torneo = Torneo(
            nombre="Torneo Test",
            fecha_inicio=timezone.now().date() + timedelta(days=10),
            fecha_fin=timezone.now().date() + timedelta(days=5),  # Antes del inicio
            premio="$1000",
            estado="INSCRIPCION"
        )
        
        with pytest.raises(ValidationError) as exc_info:
            torneo.clean()
        
        assert 'posterior' in str(exc_info.value).lower()
    
    def test_costo_inscripcion_positivo(self):
        """Test: Costo de inscripción debe ser positivo"""
        torneo = Torneo(
            nombre="Torneo Test",
            fecha_inicio=timezone.now().date() + timedelta(days=7),
            fecha_fin=timezone.now().date() + timedelta(days=14),
            premio="$1000",
            estado="INSCRIPCION",
            costo_inscripcion=-500  # Negativo
        )
        
        with pytest.raises(ValidationError) as exc_info:
            torneo.full_clean()  # full_clean valida los validators (MinValueValidator)
        
        assert 'costo' in str(exc_info.value).lower()
