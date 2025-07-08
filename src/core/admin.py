from django.contrib import admin
from .models import Cliente, Proveedor, Factura, LineaFactura

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Proveedor)

class LineaFacturaInline(admin.TabularInline): # O admin.StackedInline si prefieres un layout apilado
    model = LineaFactura
    extra = 1  # Número de líneas vacías para añadir nuevas líneas

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    inlines = [LineaFacturaInline]
    list_display = ('numero_factura', 'proveedor', 'cliente', 'fecha_emision', 'total_factura', 'importe_iva', 'importe_irpf')
    # list_filter = ('estado', 'proveedor', 'cliente', 'fecha_emision')
    search_fields = ('numero_factura', 'proveedor__nombre', 'cliente__nombre')
    date_hierarchy = 'fecha_emision'