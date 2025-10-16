from django.contrib import admin
from .models import TipoCancha, Cliente, Cancha, Servicio, Torneo, Reserva, Pago

# Registra tus modelos aquí
admin.site.register(TipoCancha)
admin.site.register(Cliente)
admin.site.register(Cancha)
admin.site.register(Servicio)
admin.site.register(Torneo)
admin.site.register(Reserva)
admin.site.register(Pago)
