from django.contrib import admin
from .models import Cliente, Proveedor, Factura, LineaFactura

# Register your models here.
admin.site.register(Cliente)


class LineaFacturaInline(admin.TabularInline):
    model = LineaFactura
    extra = 1


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    inlines = [LineaFacturaInline]
    list_display = ('numero_factura', 'proveedor', 'cliente', 'fecha_emision', 'total_factura')
    search_fields = ('numero_factura', 'proveedor__nombre', 'cliente__nombre')
    date_hierarchy = 'fecha_emision'

    def get_queryset(self, request):
        """
        Filtra las facturas para que los usuarios normales solo vean las suyas,
        mientras que los superusuarios ven todas.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(proveedor=request.user.proveedor_profile)

    def save_model(self, request, obj, form, change):
        """
        Asigna automáticamente el proveedor del usuario logueado al crear
        una nueva factura si el usuario no es superuser.
        """
        if not request.user.is_superuser:
            obj.proveedor = request.user.proveedor_profile
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        """
        Hace que el campo 'proveedor' sea de solo lectura para usuarios
        normales, para que no puedan asignarse facturas de otros.
        """
        if not request.user.is_superuser:
            return ('proveedor',)
        return ()


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cif_nif', 'user')
    search_fields = ('nombre', 'cif_nif', 'user__username')

    def get_queryset(self, request):
        """
        Filtra los perfiles de proveedor para que los usuarios normales
        solo puedan ver y editar el suyo.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)