from django.views.generic import ListView
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS

from core.models import Factura # ¡Asegúrate de que 'tu_app' sea el nombre correcto de tu app de modelos!


class FacturaListView(ListView):
    """
    Vista que muestra un listado de todas las facturas.
    """
    model = Factura
    template_name = 'backoffice/factura_list.html' # ¡Ruta de plantilla actualizada!
    context_object_name = 'facturas'
    paginate_by = 10


def generar_pdf_factura(request, factura_id):
    """
    Vista para generar y descargar la factura en formato PDF.
    """
    factura = get_object_or_404(Factura, pk=factura_id)
    html_string = render_to_string('backoffice/factura_pdf.html', {'factura': factura}) # ¡Ruta de plantilla actualizada!
    pdf_data = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{factura.numero_factura}.pdf"'
    return response