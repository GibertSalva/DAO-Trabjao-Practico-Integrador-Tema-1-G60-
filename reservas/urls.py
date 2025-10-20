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
    
    # URLs de Torneos
    path('torneos/', views.torneo_lista, name='torneo_lista'),
    path('torneos/crear/', views.torneo_crear, name='torneo_crear'),
    path('torneos/<int:pk>/', views.torneo_detalle, name='torneo_detalle'),
    path('torneos/<int:pk>/editar/', views.torneo_editar, name='torneo_editar'),
    path('torneos/<int:pk>/eliminar/', views.torneo_eliminar, name='torneo_eliminar'),
]
