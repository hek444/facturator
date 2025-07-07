# tu_app/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LineaFactura, Factura

# Cuando una LineaFactura se guarda o actualiza
@receiver(post_save, sender=LineaFactura)
def recalcular_totales_factura_on_save(sender, instance, **kwargs):
    # instance es la LineaFactura que se acaba de guardar
    # Asegúrate de que la Factura ya tenga un PK (siempre lo tendrá en post_save)
    instance.factura.calcular_totales()
    instance.factura.save()

# Cuando una LineaFactura se elimina
@receiver(post_delete, sender=LineaFactura)
def recalcular_totales_factura_on_delete(sender, instance, **kwargs):
    # instance es la LineaFactura que se acaba de eliminar
    # Necesitamos asegurarnos de que la factura padre siga existiendo
    # para evitar errores si la factura se elimina en cascada primero
    if instance.factura.pk: # Comprueba si la factura padre todavía existe
        instance.factura.calcular_totales()
        instance.factura.save()