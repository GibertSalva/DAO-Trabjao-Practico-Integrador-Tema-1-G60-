from django.urls import path
from . import views

# Aca definimos las URLs para la app 'reservas'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # URLs de Autenticación
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
    path('mis-reservas/', views.mis_reservas_view, name='mis_reservas'),
    
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
]
