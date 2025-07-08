from django.db import models
from decimal import Decimal


class Cliente(models.Model):
    nombre = models.CharField(max_length=200, help_text="Nombre o Razón Social del Cliente")
    cif_nif = models.CharField(max_length=20, unique=True, verbose_name="CIF/NIF")
    direccion = models.TextField(blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=200, help_text="Nombre o Razón Social del Proveedor")
    cif_nif = models.CharField(max_length=20, unique=True, verbose_name="CIF/NIF")
    direccion = models.TextField(blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Factura(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='facturas_emitidas_a_clientes')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='facturas_recibidas_de_proveedores')

    numero_factura = models.CharField(max_length=50, unique=True, help_text="Número único de la factura")
    fecha_emision = models.DateField(help_text="Fecha en que la factura fue emitida")
    fecha_vencimiento = models.DateField(blank=True, null=True, help_text="Fecha límite para el pago de la factura")
    base_imponible = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Base Imponible")    
    porcentaje_iva = models.DecimalField(max_digits=4, decimal_places=2, default=21.00, verbose_name="% IVA")
    porcentaje_irpf = models.DecimalField(max_digits=4, decimal_places=2, default=15.00, verbose_name="% IRPF")

    importe_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Importe IVA")
    importe_irpf = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Importe IRPF")
    total_factura = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Factura")

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado de la Factura")
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-fecha_emision', 'numero_factura']

    def __str__(self):
        return f"Factura {self.numero_factura} de {self.proveedor.nombre} para {self.cliente.nombre}"

    def calcular_totales(self):
        """
        Calcula la base imponible a partir de las líneas de factura,
        y luego el IVA, IRPF y el total de la factura.
        """
        self.base_imponible = sum(linea.importe_linea for linea in self.lineas.all())

        porcentaje_iva_decimal = Decimal(str(self.porcentaje_iva))
        porcentaje_irpf_decimal = Decimal(str(self.porcentaje_irpf))
        
        self.importe_iva = self.base_imponible * (porcentaje_iva_decimal / Decimal(100)) # ELIMINAR EL 
        self.importe_irpf = self.base_imponible * (porcentaje_irpf_decimal / Decimal(100))
        self.total_factura = self.base_imponible + self.importe_iva - self.importe_irpf


    def save(self, *args, **kwargs):
        """
        Sobreescribe el método save para asegurar que los cálculos se realicen
        antes de guardar la instancia de la factura.
        """
        super().save(*args, **kwargs)


class LineaFactura(models.Model):
    """
    Representa una línea de detalle dentro de una Factura.
    Cada factura puede tener múltiples líneas.
    """
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='lineas')
    descripcion = models.CharField(max_length=255, help_text="Descripción del concepto de la línea")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cantidad de unidades")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio por unidad")
    importe_linea = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Importe Línea")

    class Meta:
        verbose_name = "Línea de Factura"
        verbose_name_plural = "Líneas de Factura"

    def __str__(self):
        return f"{self.descripcion} ({self.cantidad} x {self.precio_unitario})"

    def save(self, *args, **kwargs):
        """
        Sobreescribe el método save para calcular el importe de la línea.
        La actualización de la factura padre se hará mediante una señal.
        """
        self.importe_linea = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)