from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from reservas.models import Cliente, TipoCancha, Cancha, Reserva, Servicio, Pago, Torneo, Equipo
from django.core.exceptions import ValidationError


class ClienteModelTests(TestCase):
    """Tests para el modelo Cliente"""

    def test_crear_cliente_valido(self):
        """Test: Se puede crear un cliente con datos válidos"""
        cliente = Cliente.objects.create(
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            email="juan@example.com",
            telefono="1234567890"
        )
        self.assertEqual(cliente.nombre, "Juan")
        self.assertEqual(cliente.dni, "12345678")
        self.assertEqual(Cliente.objects.count(), 1)

    def test_validacion_dni_duplicado(self):
        """Test: No se permite crear clientes con DNI duplicado"""
        Cliente.objects.create(
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            email="juan@example.com"
        )
        cliente2 = Cliente(
            nombre="María",
            apellido="García",
            dni="12345678",
            email="maria@example.com"
        )
        with self.assertRaises(ValidationError):
            cliente2.full_clean()

    def test_validacion_dni_todo_ceros(self):
        """Test: No se permite DNI con todos ceros"""
        cliente = Cliente(
            nombre="Test",
            apellido="User",
            dni="00000000",
            email="test@example.com"
        )
        with self.assertRaises(ValidationError):
            cliente.full_clean()

    def test_validacion_email(self):
        """Test: El email debe tener formato válido"""
        cliente = Cliente(
            nombre="Test",
            apellido="User",
            dni="12345678",
            email="email_invalido"
        )
        with self.assertRaises(ValidationError):
            cliente.full_clean()

    def test_str_representacion(self):
        """Test: La representación string del cliente es correcta"""
        cliente = Cliente.objects.create(
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            email="juan@example.com"
        )
        self.assertEqual(str(cliente), "Juan Pérez")


class CanchaModelTests(TestCase):
    """Tests para el modelo Cancha"""

    def setUp(self):
        self.tipo_cancha = TipoCancha.objects.create(
            nombre="Fútbol 5",
            descripcion="Cancha de fútbol 5"
        )

    def test_crear_cancha_valida(self):
        """Test: Se puede crear una cancha con datos válidos"""
        cancha = Cancha.objects.create(
            nombre="Cancha A",
            tipo_cancha=self.tipo_cancha,
            precio_por_hora=Decimal("5000.00")
        )
        self.assertEqual(cancha.nombre, "Cancha A")
        self.assertEqual(cancha.precio_por_hora, Decimal("5000.00"))

    def test_precio_debe_ser_positivo(self):
        """Test: El precio no puede ser negativo"""
        cancha = Cancha(
            nombre="Cancha B",
            tipo_cancha=self.tipo_cancha,
            precio_por_hora=Decimal("-100.00")
        )
        with self.assertRaises(ValidationError):
            cancha.full_clean()

    def test_str_representacion(self):
        """Test: La representación string de la cancha es correcta"""
        cancha = Cancha.objects.create(
            nombre="Cancha A",
            tipo_cancha=self.tipo_cancha,
            precio_por_hora=Decimal("5000.00")
        )
        self.assertIn("Cancha A", str(cancha))


class ReservaModelTests(TestCase):
    """Tests para el modelo Reserva"""

    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            email="juan@example.com"
        )
        self.tipo_cancha = TipoCancha.objects.create(
            nombre="Fútbol 5",
            descripcion="Cancha de fútbol 5"
        )
        self.cancha = Cancha.objects.create(
            nombre="Cancha A",
            tipo_cancha=self.tipo_cancha,
            precio_por_hora=Decimal("5000.00")
        )
        self.servicio = Servicio.objects.create(
            nombre="Iluminación",
            descripcion="Luz artificial",
            costo_adicional=Decimal("1000.00")
        )

    def test_crear_reserva_valida(self):
        """Test: Se puede crear una reserva válida"""
        fecha_inicio = timezone.now() + timedelta(days=1)
        fecha_fin = fecha_inicio + timedelta(hours=2)
        
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            cancha=self.cancha,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin,
            estado='PENDIENTE'
        )
        self.assertEqual(reserva.cliente, self.cliente)
        self.assertEqual(reserva.cancha, self.cancha)
        self.assertEqual(reserva.estado, 'PENDIENTE')

    def test_no_permite_reservar_en_pasado(self):
        """Test: No se puede reservar en el pasado"""
        fecha_inicio = timezone.now() - timedelta(days=1)
        fecha_fin = fecha_inicio + timedelta(hours=2)
        
        reserva = Reserva(
            cliente=self.cliente,
            cancha=self.cancha,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin,
            estado='PENDIENTE'
        )
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_fecha_fin_posterior_a_inicio(self):
        """Test: La fecha fin debe ser posterior a la fecha inicio"""
        fecha_inicio = timezone.now() + timedelta(days=1)
        fecha_fin = fecha_inicio - timedelta(hours=1)
        
        reserva = Reserva(
            cliente=self.cliente,
            cancha=self.cancha,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin,
            estado='PENDIENTE'
        )
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_duracion_minima_1_hora(self):
        """Test: La duración mínima de una reserva es 1 hora"""
        fecha_inicio = timezone.now() + timedelta(days=1)
        fecha_fin = fecha_inicio + timedelta(minutes=30)
        
        reserva = Reserva(
            cliente=self.cliente,
            cancha=self.cancha,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin,
            estado='PENDIENTE'
        )
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_duracion_maxima_4_horas(self):
        """Test: La duración máxima de una reserva es 4 horas"""
        fecha_inicio = timezone.now() + timedelta(days=1)
        fecha_fin = fecha_inicio + timedelta(hours=5)
        
        reserva = Reserva(
            cliente=self.cliente,
            cancha=self.cancha,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin,
            estado='PENDIENTE'
        )
        with self.assertRaises(ValidationError):
            reserva.full_clean()

    def test_calcular_costo_total(self):
        """Test: El costo total se calcula correctamente"""
        fecha_inicio = timezone.now() + timedelta(days=1)
        fecha_fin = fecha_inicio + timedelta(hours=2)
        
        reserva = Reserva.objects.create(
            cliente=self.cliente,
            cancha=self.cancha,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin,
            estado='PENDIENTE'
        )
        reserva.servicios.add(self.servicio)
        
        costo_esperado = (Decimal("5000.00") * 2) + Decimal("1000.00")
        self.assertEqual(reserva.calcular_costo_total(), costo_esperado)


class PagoModelTests(TestCase):
    """Tests para el modelo Pago"""

    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            email="juan@example.com"
        )
        self.tipo_cancha = TipoCancha.objects.create(
            nombre="Fútbol 5",
            descripcion="Cancha de fútbol 5"
        )
        self.cancha = Cancha.objects.create(
            nombre="Cancha A",
            tipo_cancha=self.tipo_cancha,
            precio_por_hora=Decimal("5000.00")
        )
        fecha_inicio = timezone.now() + timedelta(days=1)
        fecha_fin = fecha_inicio + timedelta(hours=2)
        self.reserva = Reserva.objects.create(
            cliente=self.cliente,
            cancha=self.cancha,
            fecha_hora_inicio=fecha_inicio,
            fecha_hora_fin=fecha_fin,
            estado='PENDIENTE'
        )

    def test_crear_pago_pendiente(self):
        """Test: Se puede crear un pago pendiente"""
        pago = Pago.objects.create(
            reserva=self.reserva,
            monto_total=Decimal("10000.00"),
            estado='pendiente',
            metodo_pago='efectivo'
        )
        self.assertEqual(pago.estado, 'pendiente')
        self.assertEqual(pago.monto_total, Decimal("10000.00"))

    def test_marcar_como_pagado(self):
        """Test: Se puede marcar un pago como pagado"""
        pago = Pago.objects.create(
            reserva=self.reserva,
            monto_total=Decimal("10000.00"),
            estado='pendiente',
            metodo_pago='efectivo'
        )
        pago.estado = 'pagada'
        pago.save()
        self.assertEqual(pago.estado, 'pagada')

    def test_monto_debe_ser_positivo(self):
        """Test: El monto debe ser positivo"""
        pago = Pago(
            reserva=self.reserva,
            monto_total=Decimal("-100.00"),
            estado='pendiente',
            metodo_pago='efectivo'
        )
        with self.assertRaises(ValidationError):
            pago.full_clean()


class TorneoModelTests(TestCase):
    """Tests para el modelo Torneo"""

    def setUp(self):
        self.tipo_cancha = TipoCancha.objects.create(
            nombre="Fútbol 5",
            descripcion="Cancha de fútbol 5"
        )

    def test_crear_torneo_valido(self):
        """Test: Se puede crear un torneo válido"""
        fecha_inicio = timezone.now().date() + timedelta(days=7)
        fecha_fin = fecha_inicio + timedelta(days=30)
        
        torneo = Torneo.objects.create(
            nombre="Torneo Verano 2024",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            costo_inscripcion=Decimal("5000.00")
        )
        self.assertEqual(torneo.nombre, "Torneo Verano 2024")
        self.assertEqual(torneo.estado, 'INSCRIPCION')

    def test_fecha_fin_posterior_a_inicio(self):
        """Test: La fecha fin debe ser posterior a la fecha inicio"""
        fecha_inicio = timezone.now().date() + timedelta(days=7)
        fecha_fin = fecha_inicio - timedelta(days=1)
        
        torneo = Torneo(
            nombre="Torneo Verano 2024",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        with self.assertRaises(ValidationError):
            torneo.full_clean()


class ReservaViewTests(TestCase):
    """Tests para las vistas de Reserva"""

    def setUp(self):
        self.client = Client()
        self.cliente = Cliente.objects.create(
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            email="juan@example.com"
        )
        self.tipo_cancha = TipoCancha.objects.create(
            nombre="Fútbol 5",
            descripcion="Cancha de fútbol 5"
        )
        self.cancha = Cancha.objects.create(
            nombre="Cancha A",
            tipo_cancha=self.tipo_cancha,
            precio_por_hora=Decimal("5000.00")
        )

    def test_listar_reservas(self):
        """Test: Se puede acceder a la lista de reservas"""
        response = self.client.get('/reservas/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/reservas/lista.html')

    def test_crear_reserva_get(self):
        """Test: Se puede acceder al formulario de crear reserva"""
        response = self.client.get('/reservas/crear/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/reservas/form.html')


class ClienteViewTests(TestCase):
    """Tests para las vistas de Cliente"""

    def setUp(self):
        self.client = Client()

    def test_listar_clientes(self):
        """Test: Se puede acceder a la lista de clientes"""
        response = self.client.get('/clientes/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/clientes/lista.html')

    def test_crear_cliente_get(self):
        """Test: Se puede acceder al formulario de crear cliente"""
        response = self.client.get('/clientes/crear/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/clientes/form.html')


class CanchaViewTests(TestCase):
    """Tests para las vistas de Cancha"""

    def setUp(self):
        self.client = Client()
        self.tipo_cancha = TipoCancha.objects.create(
            nombre="Fútbol 5",
            descripcion="Cancha de fútbol 5"
        )

    def test_listar_canchas(self):
        """Test: Se puede acceder a la lista de canchas"""
        response = self.client.get('/canchas/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/canchas/lista.html')

    def test_crear_cancha_get(self):
        """Test: Se puede acceder al formulario de crear cancha"""
        response = self.client.get('/canchas/crear/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/canchas/form.html')


class HomeViewTests(TestCase):
    """Tests para la vista Home"""

    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        """Test: Se puede acceder a la página principal"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/home.html')


class ReportesViewTests(TestCase):
    """Tests para las vistas de reportes"""

    def setUp(self):
        self.client = Client()

    def test_reportes_page(self):
        """Test: Se puede acceder a la página de reportes"""
        response = self.client.get('/reportes/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/reportes.html')

    def test_reportes_pdf(self):
        """Test: Se puede generar el PDF de reportes"""
        response = self.client.get('/reportes/pdf/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

