# -*- coding: utf-8 -*-
"""
Script para poblar la base de datos con superpoblación automática
Ejecutar con: python poblar_db_auto.py
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'canchas_project.settings')
django.setup()

from poblar_db import (
    limpiar_datos, 
    crear_tipos_cancha, 
    crear_clientes, 
    crear_canchas, 
    crear_servicios, 
    crear_torneos, 
    crear_reservas, 
    crear_pagos,
    superpoblar_reservas,
    mostrar_resumen
)

def main():
    """Función principal - ejecuta la población automáticamente"""
    print("\n" + "="*60)
    print("SCRIPT DE SUPERPOBLACIÓN AUTOMÁTICA")
    print("Sistema de Reservas Deportivas")
    print("Se crearán 500+ reservas para 2025")
    print("="*60)
    
    try:
        print("\nIniciando población de base de datos...")
        
        # Limpiar datos existentes
        limpiar_datos()
        
        # Crear datos base
        print("\nCreando datos base...")
        tipos_cancha = crear_tipos_cancha()
        clientes = crear_clientes()
        canchas = crear_canchas(tipos_cancha)
        servicios = crear_servicios()
        torneos = crear_torneos()
        reservas = crear_reservas(clientes, canchas, servicios, torneos)
        pagos = crear_pagos(reservas)
        
        # Crear superpoblación
        print("\nCreando superpoblación de reservas...")
        reservas_adicionales = superpoblar_reservas(clientes, canchas, servicios, torneos, 500)
        
        # Mostrar resumen
        print("\n")
        mostrar_resumen()
        
        print("\n✓ Base de datos poblada exitosamente con 500+ reservas!")
        print("  Puedes ver los reportes en: http://localhost:8000/reportes/")
        
    except Exception as e:
        print(f"\nError al poblar la base de datos: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
