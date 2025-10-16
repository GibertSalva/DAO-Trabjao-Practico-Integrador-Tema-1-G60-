from django.db import models

# --- Modelos Base ---

class TipoCancha(models.Model):

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción o reglas del tipo de cancha.")

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=10, unique=True, verbose_name="DNI")
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Cancha(models.Model):
    nombre = models.CharField(max_length=100, help_text="Ej: Cancha 1 - Central")
    tipo_cancha = models.ForeignKey(TipoCancha, on_delete=models.PROTECT, related_name="canchas")
    precio_por_hora = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} ({self.tipo_cancha.nombre})"

# --- Modelos de Complejidad Adicional ---

class Servicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    costo_adicional = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.nombre} - ${self.costo_adicional}"

class Torneo(models.Model):
    nombre = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    reglamento = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# --- Modelos Transaccionales ---

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
    ]

    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    
    # Relaciones clave
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="reservas")
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE, related_name="reservas")
    
    # Relaciones opcionales/adicionales
    servicios = models.ManyToManyField(Servicio, blank=True, related_name="reservas")
    torneo = models.ForeignKey(Torneo, on_delete=models.SET_NULL, null=True, blank=True, related_name="reservas")

    def __str__(self):
        return f"Reserva de {self.cliente} en {self.cancha.nombre} - {self.fecha_hora_inicio.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        # Evita que se pueda reservar la misma cancha en el mismo horario
        unique_together = ('cancha', 'fecha_hora_inicio')

class Pago(models.Model):
    """
    Gestiona el pago asociado a una única Reserva.
    Relación 1 a 1 con Reserva.
    """
    ESTADO_PAGO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('REEMBOLSADO', 'Reembolsado'),
    ]

    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('ONLINE', 'Online'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]

    # Relación 1 a 1: un pago por reserva
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, primary_key=True, related_name="pago")
    
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='PENDIENTE')

    def __str__(self):
        return f"Pago para la reserva {self.reserva.id} - Estado: {self.estado}"