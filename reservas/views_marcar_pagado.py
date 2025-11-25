from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Reserva


@require_http_methods(["POST"])
def reserva_marcar_como_pagado(request, pk):
    """
    Vista para marcar manualmente una reserva como pagada (solo para demo/desarrollo)
    """
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if reserva.estado != 'PENDIENTE':
        messages.warning(request, 'Esta reserva ya no está pendiente.')
        return redirect('reserva_detalle', pk=pk)
    
    if hasattr(reserva, 'pago'):
        pago = reserva.pago
        if pago.estado != 'PAGADO':
            # Marcar como pagado con método efectivo
            pago.marcar_como_pagado('EFECTIVO', 'MANUAL-DEMO')
            messages.success(request, '✅ Reserva marcada como pagada exitosamente (modo demostración).')
        else:
            messages.info(request, 'El pago ya estaba registrado como pagado.')
    else:
        messages.error(request, 'Esta reserva no tiene un pago asociado.')
    
    return redirect('reserva_detalle', pk=pk)
