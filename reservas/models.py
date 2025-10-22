from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from datetime import datetime, time, timedelta
import re

# Aca definimos los modelos para la app 'reservas', estan acordes a la estructura planteada en el diagrama ER.

# ========== CONFIGURACIÓN DE HORARIOS DEL NEGOCIO ==========
HORA_APERTURA = time(8, 0)  # 8:00 AM
HORA_CIERRE = time(23, 0)   # 11:00 PM
DURACION_MINIMA_RESERVA = 1  # 1 hora
DURACION_MAXIMA_RESERVA = 4  # 4 horas
MAX_RESERVAS_POR_CLIENTE_DIA = 3  # Máximo 3 reservas por día por cliente

# ========== VALIDADORES PERSONALIZADOS ==========

def validar_dni_argentino(value):
    """Valida que el DNI tenga formato argentino (7-8 dígitos)"""
    if not re.match(r'^\d{7,8}$', value):
        raise ValidationError('El DNI debe tener 7 u 8 dígitos numéricos.')

def validar_telefono(value):
    """Valida formato de teléfono argentino"""
    if not re.match(r'^[\d\s\-\+\(\)]{8,20}$', value):
        raise ValidationError('Ingrese un número de teléfono válido.')

# --- Modelos Base ---

class TipoCancha(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción o reglas del tipo de cancha.")

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Tipo de Cancha"
        verbose_name_plural = "Tipos de Cancha"
        ordering = ['nombre']

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(
        max_length=10, 
        unique=True, 
        verbose_name="DNI",
        validators=[validar_dni_argentino],
        help_text="DNI argentino de 7 u 8 dígitos"
    )
    email = models.EmailField(unique=True, help_text="Email único para el cliente")
    telefono = models.CharField(
        max_length=20,
        validators=[validar_telefono],
        help_text="Número de teléfono válido"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True, help_text="Cliente activo en el sistema")

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    def clean(self):
        """Validaciones personalizadas a nivel de modelo"""
        super().clean()
        
        # Validar que nombre y apellido no tengan números
        if any(char.isdigit() for char in self.nombre):
            raise ValidationError({'nombre': 'El nombre no puede contener números.'})
        
        if any(char.isdigit() for char in self.apellido):
            raise ValidationError({'apellido': 'El apellido no puede contener números.'})
        
        # Normalizar: Primera letra mayúscula
        self.nombre = self.nombre.strip().title()
        self.apellido = self.apellido.strip().title()
    
    def puede_reservar(self, fecha):
        """Verifica si el cliente puede hacer más reservas en una fecha determinada"""
        reservas_dia = self.reservas.filter(
            fecha_hora_inicio__date=fecha,
            estado__in=['PENDIENTE', 'PAGADA']
        ).count()
        return reservas_dia < MAX_RESERVAS_POR_CLIENTE_DIA
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['apellido', 'nombre']

class Cancha(models.Model):
    nombre = models.CharField(max_length=100, help_text="Ej: Cancha 1 - Central")
    tipo_cancha = models.ForeignKey(TipoCancha, on_delete=models.PROTECT, related_name="canchas")
    precio_por_hora = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Precio por hora en pesos"
    )
    activa = models.BooleanField(default=True, help_text="Cancha disponible para reservas")
    capacidad_personas = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(2), MaxValueValidator(50)],
        help_text="Capacidad máxima de personas"
    )

    def __str__(self):
        return f"{self.nombre} ({self.tipo_cancha.nombre})"
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        if self.precio_por_hora and self.precio_por_hora <= 0:
            raise ValidationError({'precio_por_hora': 'El precio debe ser mayor a cero.'})
    
    def esta_disponible(self, fecha_inicio, fecha_fin):
        """Verifica si la cancha está disponible en un rango de fechas"""
        if not self.activa:
            return False
        
        reservas_conflicto = self.reservas.filter(
            estado__in=['PENDIENTE', 'PAGADA']
        ).filter(
            models.Q(fecha_hora_inicio__lt=fecha_fin) & 
            models.Q(fecha_hora_fin__gt=fecha_inicio)
        )
        
        return not reservas_conflicto.exists()
    
    class Meta:
        verbose_name = "Cancha"
        verbose_name_plural = "Canchas"
        ordering = ['nombre']

# --- Modelos de Complejidad Adicional ---

class Servicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    costo_adicional = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    activo = models.BooleanField(default=True, help_text="Servicio disponible")
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - ${self.costo_adicional}"
    
    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['nombre']

class Torneo(models.Model):
    ESTADO_CHOICES = [
        ('INSCRIPCION', 'Abierto para Inscripciones'),
        ('EN_CURSO', 'En Curso'),
        ('FINALIZADO', 'Finalizado'),
    ]
    
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción del torneo")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    premio = models.CharField(max_length=200, blank=True, null=True, help_text="Premio del torneo")
    costo_inscripcion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Costo de inscripción al torneo"
    )
    reglamento = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='INSCRIPCION',
        help_text="Estado actual del torneo"
    )
    equipos = models.ManyToManyField(
        'Equipo', 
        blank=True, 
        related_name='torneos',
        help_text="Equipos inscritos en el torneo"
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
    def clean(self):
        """Validaciones de fechas del torneo"""
        super().clean()
        
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_fin < self.fecha_inicio:
                raise ValidationError({
                    'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
                })
    
    def equipos_count(self):
        """Retorna la cantidad de equipos inscritos"""
        return self.equipos.count()
    
    def puede_agregar_equipos(self):
        """Verifica si se pueden agregar equipos (solo si está en inscripción)"""
        return self.estado == 'INSCRIPCION'
    
    def generar_fixture(self):
        """Genera el fixture de eliminación directa"""
        if self.estado != 'INSCRIPCION':
            raise ValidationError('Solo se puede generar el fixture si el torneo está en inscripción.')
        
        equipos_list = list(self.equipos.all())
        num_equipos = len(equipos_list)
        
        if num_equipos < 2:
            raise ValidationError('Se necesitan al menos 2 equipos para generar el fixture.')
        
        # Verificar que sea potencia de 2 (2, 4, 8, 16, etc.)
        import math
        if num_equipos & (num_equipos - 1) != 0:
            raise ValidationError(f'El número de equipos debe ser potencia de 2 (2, 4, 8, 16...). Tienes {num_equipos} equipos.')
        
        # Eliminar partidos anteriores si existen
        self.partidos.all().delete()
        
        # Calcular número de rondas
        num_rondas = int(math.log2(num_equipos))
        
        # Crear primera ronda
        import random
        random.shuffle(equipos_list)
        
        ronda = 1
        for i in range(0, num_equipos, 2):
            Partido.objects.create(
                torneo=self,
                equipo1=equipos_list[i],
                equipo2=equipos_list[i + 1],
                ronda=ronda,
                numero_partido=(i // 2) + 1
            )
        
        # Cambiar estado del torneo
        self.estado = 'EN_CURSO'
        self.save()
    
    class Meta:
        verbose_name = "Torneo"
        verbose_name_plural = "Torneos"
        ordering = ['-fecha_inicio']

class Equipo(models.Model):
    """Modelo para gestionar equipos independientes"""
    nombre = models.CharField(max_length=150, unique=True, help_text="Nombre del equipo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True, help_text="Equipo activo")
    logo = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        help_text="Emoji o icono para el equipo (opcional)"
    )
    
    def __str__(self):
        return self.nombre
    
    def clean(self):
        """Validaciones del equipo"""
        super().clean()
        
        # Validar nombre único
        if self.pk:
            if Equipo.objects.filter(nombre__iexact=self.nombre).exclude(pk=self.pk).exists():
                raise ValidationError({
                    'nombre': f'Ya existe un equipo con el nombre "{self.nombre}".'
                })
    
    def torneos_activos(self):
        """Retorna los torneos activos en los que participa"""
        return self.torneos.filter(activo=True)
    
    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['nombre']

class Partido(models.Model):
    """Modelo para representar un partido del torneo (eliminación directa)"""
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('FINALIZADO', 'Finalizado'),
        ('WALKOVER', 'Walkover'),  # Un equipo no se presentó
    ]
    
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE, related_name='partidos')
    ronda = models.PositiveIntegerField(help_text="Ronda del torneo (1=Primera ronda, 2=Semifinal, etc.)")
    numero_partido = models.PositiveIntegerField(help_text="Número de partido dentro de la ronda")
    
    equipo1 = models.ForeignKey(
        Equipo, 
        on_delete=models.CASCADE, 
        related_name='partidos_como_equipo1',
        null=True,
        blank=True,
        help_text="Primer equipo (puede ser null si viene de un partido anterior)"
    )
    equipo2 = models.ForeignKey(
        Equipo, 
        on_delete=models.CASCADE, 
        related_name='partidos_como_equipo2',
        null=True,
        blank=True,
        help_text="Segundo equipo (puede ser null si viene de un partido anterior)"
    )
    
    resultado_equipo1 = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Resultado del equipo 1"
    )
    resultado_equipo2 = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Resultado del equipo 2"
    )
    
    ganador = models.ForeignKey(
        Equipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partidos_ganados',
        help_text="Equipo ganador"
    )
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_hora = models.DateTimeField(null=True, blank=True, help_text="Fecha y hora del partido")
    observaciones = models.TextField(blank=True, null=True)
    
    # Para saber de qué partidos vienen los equipos (en rondas posteriores)
    partido_anterior_equipo1 = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='siguiente_partido_ganador1'
    )
    partido_anterior_equipo2 = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='siguiente_partido_ganador2'
    )
    
    def __str__(self):
        e1 = self.equipo1.nombre if self.equipo1 else 'TBD'
        e2 = self.equipo2.nombre if self.equipo2 else 'TBD'
        return f"{self.torneo.nombre} - Ronda {self.ronda} - {e1} vs {e2}"
    
    def clean(self):
        """Validaciones del partido"""
        super().clean()
        
        # Si hay resultados, ambos deben estar presentes
        if (self.resultado_equipo1 is not None) != (self.resultado_equipo2 is not None):
            raise ValidationError('Debe ingresar el resultado de ambos equipos.')
        
        # Si hay resultados, debe haber un ganador
        if self.resultado_equipo1 is not None and self.resultado_equipo2 is not None:
            if self.resultado_equipo1 == self.resultado_equipo2:
                raise ValidationError('No puede haber empate en eliminación directa. Debe haber un ganador.')
            
            # Determinar ganador automáticamente
            if self.resultado_equipo1 > self.resultado_equipo2:
                self.ganador = self.equipo1
            else:
                self.ganador = self.equipo2
            
            self.estado = 'FINALIZADO'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Si este partido tiene ganador, actualizar el siguiente partido
        if self.ganador and self.estado == 'FINALIZADO':
            self.avanzar_ganador()
    
    def avanzar_ganador(self):
        """Avanza al ganador a la siguiente ronda"""
        # Buscar el partido de la siguiente ronda
        siguiente_ronda = self.ronda + 1
        numero_siguiente = (self.numero_partido + 1) // 2
        
        try:
            siguiente_partido = Partido.objects.get(
                torneo=self.torneo,
                ronda=siguiente_ronda,
                numero_partido=numero_siguiente
            )
            
            # Determinar si va como equipo1 o equipo2
            if self.numero_partido % 2 == 1:  # Impar -> equipo1
                siguiente_partido.equipo1 = self.ganador
                siguiente_partido.partido_anterior_equipo1 = self
            else:  # Par -> equipo2
                siguiente_partido.equipo2 = self.ganador
                siguiente_partido.partido_anterior_equipo2 = self
            
            siguiente_partido.save()
        except Partido.DoesNotExist:
            # Es la final, no hay siguiente partido
            pass
    
    def nombre_ronda(self):
        """Retorna el nombre de la ronda"""
        total_equipos = self.torneo.equipos.count()
        import math
        total_rondas = int(math.log2(total_equipos)) if total_equipos > 0 else 0
        
        if self.ronda == total_rondas:
            return "Final"
        elif self.ronda == total_rondas - 1:
            return "Semifinal"
        elif self.ronda == total_rondas - 2:
            return "Cuartos de Final"
        else:
            return f"Ronda {self.ronda}"
    
    def get_ronda_display(self):
        """Alias de nombre_ronda para compatibilidad con templates"""
        return self.nombre_ronda()
    
    @property
    def siguiente_partido(self):
        """Obtiene el partido de la siguiente ronda al que avanzará el ganador"""
        siguiente_ronda = self.ronda + 1
        numero_siguiente = (self.numero_partido + 1) // 2
        
        try:
            return Partido.objects.get(
                torneo=self.torneo,
                ronda=siguiente_ronda,
                numero_partido=numero_siguiente
            )
        except Partido.DoesNotExist:
            return None
    
    class Meta:
        verbose_name = "Partido"
        verbose_name_plural = "Partidos"
        ordering = ['torneo', 'ronda', 'numero_partido']
        unique_together = ('torneo', 'ronda', 'numero_partido')

# --- Modelos Transaccionales ---

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('CANCELADA', 'Cancelada'),
    ]

    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Relaciones clave
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="reservas")
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE, related_name="reservas")
    
    # Relaciones opcionales/adicionales
    servicios = models.ManyToManyField(Servicio, blank=True, related_name="reservas")
    torneo = models.ForeignKey(Torneo, on_delete=models.SET_NULL, null=True, blank=True, related_name="reservas")
    
    # Observaciones
    observaciones = models.TextField(blank=True, null=True, help_text="Notas adicionales sobre la reserva")

    def __str__(self):
        return f"Reserva de {self.cliente} en {self.cancha.nombre} - {self.fecha_hora_inicio.strftime('%d/%m/%Y %H:%M')}"

    def clean(self):
        """Validaciones exhaustivas de la reserva"""
        super().clean()
        
        if not self.fecha_hora_inicio or not self.fecha_hora_fin:
            return
        
        # 1. Validar que la fecha de fin sea posterior a la de inicio
        if self.fecha_hora_fin <= self.fecha_hora_inicio:
            raise ValidationError({
                'fecha_hora_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
        
        # 2. Validar que no se reserve en el pasado
        if self.fecha_hora_inicio < timezone.now():
            raise ValidationError({
                'fecha_hora_inicio': 'No se pueden hacer reservas en el pasado.'
            })
        
        # 3. Validar horario de apertura/cierre
        if self.fecha_hora_inicio.time() < HORA_APERTURA:
            raise ValidationError({
                'fecha_hora_inicio': f'El complejo abre a las {HORA_APERTURA.strftime("%H:%M")}.'
            })
        
        if self.fecha_hora_fin.time() > HORA_CIERRE:
            raise ValidationError({
                'fecha_hora_fin': f'El complejo cierra a las {HORA_CIERRE.strftime("%H:%M")}.'
            })
        
        # 4. Validar duración de la reserva
        duracion = (self.fecha_hora_fin - self.fecha_hora_inicio).total_seconds() / 3600
        
        if duracion < DURACION_MINIMA_RESERVA:
            raise ValidationError({
                'fecha_hora_fin': f'La duración mínima de una reserva es de {DURACION_MINIMA_RESERVA} hora(s).'
            })
        
        if duracion > DURACION_MAXIMA_RESERVA:
            raise ValidationError({
                'fecha_hora_fin': f'La duración máxima de una reserva es de {DURACION_MAXIMA_RESERVA} horas.'
            })
        
        # 5. Validar que las fechas sean del mismo día
        if self.fecha_hora_inicio.date() != self.fecha_hora_fin.date():
            raise ValidationError({
                'fecha_hora_fin': 'Una reserva no puede abarcar más de un día.'
            })
        
        # 6. Validar disponibilidad de la cancha (solo si no está cancelada)
        if self.estado in ['PENDIENTE', 'PAGADA'] and self.cancha_id:
            reservas_conflicto = Reserva.objects.filter(
                cancha=self.cancha,
                estado__in=['PENDIENTE', 'PAGADA']
            ).filter(
                models.Q(fecha_hora_inicio__lt=self.fecha_hora_fin) & 
                models.Q(fecha_hora_fin__gt=self.fecha_hora_inicio)
            ).exclude(pk=self.pk)  # Excluir la reserva actual si estamos editando
            
            if reservas_conflicto.exists():
                raise ValidationError({
                    'cancha': 'La cancha no está disponible en el horario seleccionado.'
                })
        
        # 7. Validar límite de reservas del cliente
        if self.cliente_id and not self.cliente.puede_reservar(self.fecha_hora_inicio.date()):
            raise ValidationError({
                'cliente': f'El cliente ya alcanzó el límite de {MAX_RESERVAS_POR_CLIENTE_DIA} reservas para este día.'
            })
        
        # 8. Validar que la cancha esté activa
        if self.cancha_id and not self.cancha.activa:
            raise ValidationError({
                'cancha': 'Esta cancha no está disponible para reservas.'
            })
        
        # 9. Validar que el cliente esté activo
        if self.cliente_id and not self.cliente.activo:
            raise ValidationError({
                'cliente': 'Este cliente no está activo en el sistema.'
            })
    
    def calcular_costo_total(self):
        """Calcula el costo total de la reserva (cancha + servicios)"""
        if not self.fecha_hora_inicio or not self.fecha_hora_fin:
            return 0
        
        # Costo de la cancha
        horas = (self.fecha_hora_fin - self.fecha_hora_inicio).total_seconds() / 3600
        costo_cancha = float(self.cancha.precio_por_hora) * horas
        
        # Costo de servicios adicionales
        costo_servicios = sum(float(s.costo_adicional) for s in self.servicios.all())
        
        return costo_cancha + costo_servicios
    
    def duracion_horas(self):
        """Retorna la duración de la reserva en horas"""
        if not self.fecha_hora_inicio or not self.fecha_hora_fin:
            return 0
        return (self.fecha_hora_fin - self.fecha_hora_inicio).total_seconds() / 3600

    class Meta:
        # Evita que se pueda reservar la misma cancha en el mismo horario
        unique_together = ('cancha', 'fecha_hora_inicio')
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_hora_inicio']

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
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
    ]

    # Relación 1 a 1: un pago por reserva
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, primary_key=True, related_name="pago")
    
    monto_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(999999.99)],
        help_text="Monto total del pago (máximo: $999,999.99)"
    )
    fecha_pago = models.DateTimeField(null=True, blank=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='PENDIENTE')
    
    # Campos adicionales
    comprobante = models.CharField(max_length=100, blank=True, null=True, help_text="Número de comprobante o transacción")
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pago para la reserva {self.reserva.id} - Estado: {self.estado}"
    
    def clean(self):
        """Validaciones del pago"""
        super().clean()
        
        # Si el pago está marcado como PAGADO, debe tener fecha y método
        if self.estado == 'PAGADO':
            if not self.fecha_pago:
                raise ValidationError({
                    'fecha_pago': 'Debe especificar la fecha de pago.'
                })
            if not self.metodo_pago:
                raise ValidationError({
                    'metodo_pago': 'Debe especificar el método de pago.'
                })
        
        # Validar que el monto sea mayor a cero
        if self.monto_total and self.monto_total <= 0:
            raise ValidationError({
                'monto_total': 'El monto debe ser mayor a cero.'
            })
    
    def marcar_como_pagado(self, metodo_pago, comprobante=None):
        """Marca el pago como pagado y actualiza la reserva"""
        self.estado = 'PAGADO'
        self.fecha_pago = timezone.now()
        self.metodo_pago = metodo_pago
        if comprobante:
            self.comprobante = comprobante
        self.save()
        
        # Actualizar estado de la reserva
        if self.reserva.estado == 'PENDIENTE':
            self.reserva.estado = 'PAGADA'
            self.reserva.save()
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"