from django.contrib import admin
from django.utils.html import format_html
from .models import TipoCancha, Cliente, Cancha, Servicio, Torneo, Reserva, Pago, Equipo, Partido

# ========== CONFIGURACIÓN MEJORADA DEL ADMIN ==========

@admin.register(TipoCancha)
class TipoCanchaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['apellido', 'nombre', 'dni', 'email', 'telefono', 'activo', 'fecha_registro']
    list_filter = ['activo', 'fecha_registro']
    search_fields = ['nombre', 'apellido', 'dni', 'email']
    ordering = ['apellido', 'nombre']

@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_cancha', 'precio_por_hora', 'capacidad_personas', 'activa']
    list_filter = ['tipo_cancha', 'activa']
    search_fields = ['nombre']
    ordering = ['nombre']

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'costo_adicional', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']
    ordering = ['nombre']

@admin.register(Torneo)
class TorneoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'fecha_inicio', 'fecha_fin', 'estado', 'costo_inscripcion', 'equipos_count', 'activo']
    list_filter = ['estado', 'activo', 'fecha_inicio']
    search_fields = ['nombre']
    filter_horizontal = ['equipos']
    ordering = ['-fecha_inicio']
    
    def equipos_count(self, obj):
        return obj.equipos.count()
    equipos_count.short_description = 'Equipos'

class PagoInline(admin.StackedInline):
    model = Pago
    can_delete = False
    extra = 0
    fields = ['monto_total', 'estado', 'metodo_pago', 'fecha_pago', 'comprobante', 'observaciones']

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'cancha', 'fecha_hora_inicio', 'fecha_hora_fin', 'estado', 'get_monto_total']
    list_filter = ['estado', 'fecha_hora_inicio', 'cancha', 'torneo']
    search_fields = ['cliente__nombre', 'cliente__apellido', 'cliente__dni', 'cancha__nombre']
    date_hierarchy = 'fecha_hora_inicio'
    ordering = ['-fecha_hora_inicio']
    filter_horizontal = ['servicios']
    inlines = [PagoInline]
    
    def get_monto_total(self, obj):
        try:
            if hasattr(obj, 'pago'):
                return format_html('<strong>${:,.2f}</strong>', float(obj.pago.monto_total))
            return '-'
        except Exception:
            return format_html('<span style="color: red;">Error</span>')
    get_monto_total.short_description = 'Monto Total'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('cliente', 'cancha', 'estado')
        }),
        ('Fechas y Horarios', {
            'fields': ('fecha_hora_inicio', 'fecha_hora_fin')
        }),
        ('Detalles Adicionales', {
            'fields': ('servicios', 'torneo', 'observaciones'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'monto_total', 'estado', 'metodo_pago', 'fecha_pago']
    list_filter = ['estado', 'metodo_pago', 'fecha_pago']
    search_fields = ['reserva__cliente__nombre', 'reserva__cliente__apellido', 'comprobante']
    ordering = ['-fecha_pago']
    readonly_fields = ['reserva']
    
    fieldsets = (
        ('Información de Pago', {
            'fields': ('reserva', 'monto_total', 'estado')
        }),
        ('Detalles de Transacción', {
            'fields': ('metodo_pago', 'fecha_pago', 'comprobante', 'observaciones')
        }),
    )

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capitan', 'jugadores_count', 'fecha_creacion', 'activo']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'capitan__nombre', 'capitan__apellido']
    filter_horizontal = ['jugadores']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información del Equipo', {
            'fields': ('nombre', 'logo', 'activo')
        }),
        ('Miembros del Equipo', {
            'fields': ('capitan', 'jugadores')
        }),
    )

@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ['torneo', 'nombre_ronda', 'equipo1', 'equipo2', 'resultado_display', 'ganador', 'estado']
    list_filter = ['torneo', 'estado', 'ronda']
    search_fields = ['torneo__nombre', 'equipo1__nombre', 'equipo2__nombre']
    ordering = ['torneo', 'ronda', 'numero_partido']
    
    fieldsets = (
        ('Información del Partido', {
            'fields': ('torneo', 'ronda', 'numero_partido', 'fecha_hora')
        }),
        ('Equipos', {
            'fields': ('equipo1', 'equipo2')
        }),
        ('Resultado', {
            'fields': ('resultado_equipo1', 'resultado_equipo2', 'ganador', 'estado')
        }),
        ('Referencias', {
            'fields': ('partido_anterior_equipo1', 'partido_anterior_equipo2', 'observaciones'),
            'classes': ('collapse',)
        }),
    )
    
    def resultado_display(self, obj):
        if obj.resultado_equipo1 is not None and obj.resultado_equipo2 is not None:
            return f"{obj.resultado_equipo1} - {obj.resultado_equipo2}"
        return "-"
    resultado_display.short_description = 'Resultado'


