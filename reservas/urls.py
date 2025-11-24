from django.urls import path
from . import views

# Aca definimos las URLs para la app 'reservas'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Reportes
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/pdf/', views.reportes_pdf, name='reportes_pdf'),
    
    # URLs de Clientes
    path('clientes/', views.cliente_lista, name='cliente_lista'),
    path('clientes/crear/', views.cliente_crear, name='cliente_crear'),
    path('clientes/<int:pk>/', views.cliente_detalle, name='cliente_detalle'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),
    path('clientes/<int:pk>/eliminar/', views.cliente_eliminar, name='cliente_eliminar'),
    
    # URLs de Canchas
    path('canchas/', views.cancha_lista, name='cancha_lista'),
    path('canchas/crear/', views.cancha_crear, name='cancha_crear'),
    path('canchas/<int:pk>/', views.cancha_detalle, name='cancha_detalle'),
    path('canchas/<int:pk>/editar/', views.cancha_editar, name='cancha_editar'),
    path('canchas/<int:pk>/eliminar/', views.cancha_eliminar, name='cancha_eliminar'),
    
    # URLs de Reservas
    path('reservas/', views.reserva_lista, name='reserva_lista'),
    path('reservas/crear/', views.reserva_crear, name='reserva_crear'),
    path('reservas/<int:pk>/', views.reserva_detalle, name='reserva_detalle'),
    path('reservas/<int:pk>/editar/', views.reserva_editar, name='reserva_editar'),
    path('reservas/<int:pk>/eliminar/', views.reserva_eliminar, name='reserva_eliminar'),
    path('reservas/<int:pk>/marcar-pagada/', views.reserva_marcar_pagada, name='reserva_marcar_pagada'),
    
    # URLs de MercadoPago
    path('reservas/<int:pk>/pagar-mercadopago/', views.reserva_crear_pago_mercadopago, name='reserva_pagar_mercadopago'),
    path('reservas/<int:pk>/pago-exitoso/', views.reserva_pago_exitoso, name='reserva_pago_exitoso'),
    path('reservas/<int:pk>/pago-pendiente/', views.reserva_pago_pendiente, name='reserva_pago_pendiente'),
    path('reservas/<int:pk>/pago-fallido/', views.reserva_pago_fallido, name='reserva_pago_fallido'),
    path('mercadopago/webhook/', views.mercadopago_webhook, name='mercadopago_webhook'),
    
    # URLs de Torneos
    path('torneos/', views.torneo_lista, name='torneo_lista'),
    path('torneos/crear/', views.torneo_crear, name='torneo_crear'),
    path('torneos/<int:pk>/', views.torneo_detalle, name='torneo_detalle'),
    path('torneos/<int:pk>/editar/', views.torneo_editar, name='torneo_editar'),
    path('torneos/<int:pk>/eliminar/', views.torneo_eliminar, name='torneo_eliminar'),
    path('torneos/<int:pk>/inscribir/', views.torneo_inscribir_equipo, name='torneo_inscribir_equipo'),
    path('torneos/<int:pk>/desinscribir/<int:equipo_pk>/', views.torneo_desinscribir_equipo, name='torneo_desinscribir_equipo'),
    path('torneos/<int:pk>/generar-fixture/', views.torneo_generar_fixture, name='torneo_generar_fixture'),
    path('torneos/<int:pk>/fixture/', views.torneo_fixture, name='torneo_fixture'),
    
    # URLs de Equipos (independientes)
    path('equipos/', views.equipo_lista, name='equipo_lista'),
    path('equipos/crear/', views.equipo_crear, name='equipo_crear'),
    path('equipos/<int:pk>/', views.equipo_detalle, name='equipo_detalle'),
    path('equipos/<int:pk>/editar/', views.equipo_editar, name='equipo_editar'),
    path('equipos/<int:pk>/eliminar/', views.equipo_eliminar, name='equipo_eliminar'),
    
    # URLs de Partidos
    path('partidos/<int:pk>/registrar-resultado/', views.partido_registrar_resultado, name='partido_registrar_resultado'),
]
