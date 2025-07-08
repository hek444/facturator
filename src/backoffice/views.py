from django.views.generic import ListView
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML, CSS
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from datetime import date
from django.urls import reverse
from django.views.generic.base import RedirectView

from core.models import Factura


class HomeRedirectView(RedirectView):
    """
    Redirige desde la página de inicio (raíz) a la lista de facturas
    del año en curso.
    """
    permanent = False 

    def get_redirect_url(self, *args, **kwargs):
        current_year = date.today().year
        return reverse('backoffice:factura_list_by_year', kwargs={'year': current_year})


class FacturaListView(LoginRequiredMixin, ListView):
    """
    Vista que muestra un listado de todas las facturas.
    """
    model = Factura
    template_name = 'backoffice/factura_list.html'
    context_object_name = 'facturas'
    paginate_by = 12

    def get_queryset(self):
        """
        Este método ahora filtra las facturas basándose en el tipo de usuario
        y el año seleccionado.
        """
        user = self.request.user
        if user.is_superuser:
            queryset = Factura.objects.all()
        else:
            try:
                queryset = Factura.objects.filter(proveedor=user.proveedor_profile)
            except AttributeError:
                queryset = Factura.objects.none()

        year = self.kwargs.get('year')
        if year:
            queryset = queryset.filter(fecha_emision__year=year)

        return queryset.order_by('-fecha_emision')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        year_str = self.kwargs.get('year')
        context['selected_year'] = int(year_str) if year_str else None
        
        context['available_years'] = Factura.objects.dates('fecha_emision', 'year', order='DESC')
        return context



def generar_pdf_factura(request, factura_id):
    """
    Vista para generar y descargar la factura en formato PDF.
    """
    factura = get_object_or_404(Factura, pk=factura_id)
    html_string = render_to_string('backoffice/factura_pdf.html', {'factura': factura})
    pdf_data = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{factura.numero_factura}.pdf"'
    return response


@login_required
def login_redirect_view(request):
    """
    Esta vista se ejecuta justo después del login.
    Calcula el año actual y redirige a la lista de facturas de ese año.
    """
    current_year = date.today().year
    return redirect('backoffice:factura_list_by_year', year=current_year)