from django.core.management.base import BaseCommand
from django.utils import timezone
from reservas.models import Equipo, Cliente
import random

class Command(BaseCommand):
    help = 'Poblar la base de datos con 20 equipos de ejemplo'

    def handle(self, *args, **kwargs):
        # Nombres de equipos variados y creativos
        nombres_equipos = [
            "Los Tigres", "Águilas FC", "Leones United", "Dragones Rojos", "Panteras Negras",
            "Lobos del Sur", "Halcones FC", "Tiburones", "Pumas Salvajes", "Cóndores",
            "Jaguares FC", "Cobras Venenosas", "Búfalos", "Osos Pardos", "Zorros Plateados",
            "Rinocerontes", "Gorilas FC", "Águilas Doradas", "Escorpiones", "Rayos del Norte"
        ]
        
        # Emojis/logos para los equipos
        logos = [
            "🐯", "🦅", "🦁", "🐉", "🐆",
            "🐺", "🦅", "🦈", "🐆", "🦅",
            "🐆", "🐍", "🦬", "🐻", "🦊",
            "🦏", "🦍", "🦅", "🦂", "⚡"
        ]
        
        # Obtener todos los clientes activos
        clientes = list(Cliente.objects.filter(activo=True))
        
        if not clientes:
            self.stdout.write(self.style.WARNING('No hay clientes en la base de datos. Creando algunos...'))
            # Crear algunos clientes de ejemplo
            nombres = ["Juan", "María", "Carlos", "Ana", "Pedro", "Laura", "Diego", "Sofia", "Miguel", "Valentina"]
            apellidos = ["García", "Rodríguez", "López", "Martínez", "González", "Pérez", "Sánchez", "Ramírez", "Torres", "Flores"]
            
            for i in range(20):
                Cliente.objects.create(
                    nombre=random.choice(nombres),
                    apellido=random.choice(apellidos),
                    dni=f"{20000000 + i}",
                    email=f"cliente{i}@example.com",
                    telefono=f"1123456{i:03d}",
                    activo=True
                )
            clientes = list(Cliente.objects.filter(activo=True))
            self.stdout.write(self.style.SUCCESS(f'Creados {len(clientes)} clientes de ejemplo'))
        
        equipos_creados = 0
        
        for i in range(20):
            nombre = nombres_equipos[i]
            logo = logos[i]
            
            # Verificar si ya existe un equipo con ese nombre
            if Equipo.objects.filter(nombre=nombre).exists():
                self.stdout.write(self.style.WARNING(f'El equipo "{nombre}" ya existe, saltando...'))
                continue
            
            # Seleccionar capitán aleatorio
            capitan = random.choice(clientes) if clientes and random.random() > 0.2 else None
            
            # Crear equipo
            equipo = Equipo.objects.create(
                nombre=nombre,
                logo=logo,
                capitan=capitan,
                fecha_creacion=timezone.now(),
                activo=True
            )
            
            # Agregar jugadores aleatorios (entre 3 y 8 jugadores)
            if clientes:
                num_jugadores = random.randint(3, min(8, len(clientes)))
                jugadores = random.sample(clientes, num_jugadores)
                equipo.jugadores.set(jugadores)
            
            equipos_creados += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Equipo creado: {logo} {nombre} - '
                    f'{equipo.jugadores.count()} jugadores'
                    f'{" - Capitán: " + capitan.nombre if capitan else ""}'
                )
            )
        
        self.stdout.write(self.style.SUCCESS(f'\n¡Proceso completado! {equipos_creados} equipos creados.'))
        self.stdout.write(self.style.SUCCESS(f'Total de equipos en la BD: {Equipo.objects.count()}'))
