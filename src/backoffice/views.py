from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.base import RedirectView
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import Sum
from django.db.models.functions import TruncMonth, Extract
from weasyprint import HTML, CSS
from datetime import date
import json

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
    model = Factura
    template_name = 'backoffice/factura_list.html'
    context_object_name = 'facturas'
    paginate_by = 12

    def get_queryset(self):
        """
        Filtra las facturas por usuario, y opcionalmente por año y trimestre.
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
        quarter = self.kwargs.get('quarter')

        if year:
            queryset = queryset.filter(fecha_emision__year=year)
        if quarter:
            queryset = queryset.filter(fecha_emision__quarter=quarter)

        return queryset.order_by('-fecha_emision')

    def get_context_data(self, **kwargs):
        """
        Añade variables extra al contexto para usarlas en la plantilla (títulos, etc.).
        """
        context = super().get_context_data(**kwargs)
        year = self.kwargs.get('year')
        quarter = self.kwargs.get('quarter')

        context['selected_year'] = year
        context['selected_quarter'] = quarter
        
        if year and quarter:
            context['titulo'] = f"Facturas de {year} - Trimestre {quarter}"
        elif year:
            context['titulo'] = f"Facturas de {year}"
        else:
            context['titulo'] = "Todas las Facturas"
            
        if self.request.GET.get('from') == 'iva':
            context['show_back_to_iva_button'] = True

        context['available_years'] = Factura.objects.dates('fecha_emision', 'year', order='DESC')
        return context


class FacturaDetailView(LoginRequiredMixin, DetailView):
    """
    Muestra los detalles de una única factura, buscando un template
    específico para el proveedor antes de usar el de por defecto.
    """
    model = Factura
    context_object_name = 'factura'

    def get_template_names(self):
        """
        Devuelve una lista de templates a intentar.
        Django usará el primero que encuentre.
        """
        user = self.request.user
        templates = ['backoffice/factura_pdf.html']

        if not user.is_superuser and hasattr(user, 'proveedor_profile'):
            provider_id = user.proveedor_profile.id
            specific_template = f'backoffice/factura_pdf_{provider_id}.html'
            templates.insert(0, specific_template)
            
        return templates

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.is_superuser:
            return qs
        try:
            return qs.filter(proveedor=user.proveedor_profile)
        except AttributeError:
            return qs.none()


@login_required
def generar_pdf_factura(request, factura_id):
    """
    Vista para generar y descargar la factura en formato PDF,
    buscando un template específico para el proveedor.
    """
    factura = get_object_or_404(Factura, pk=factura_id)
    
    user = request.user
    template_names = ['backoffice/factura_pdf.html']
    
    if not user.is_superuser and hasattr(user, 'proveedor_profile'):
        provider_id = user.proveedor_profile.id
        specific_template = f'backoffice/factura_pdf_{provider_id}.html'
        template_names.insert(0, specific_template)

    html_string = render_to_string(template_names, {'factura': factura})
    
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


class FacturacionEvolucionView(LoginRequiredMixin, TemplateView):
    """
    Muestra un gráfico con la evolución de la facturación mensual.
    """
    template_name = 'backoffice/facturacion_evolucion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

        data = queryset.annotate(month=TruncMonth('fecha_emision')).values('month').annotate(total_facturado=Sum('total_factura')).order_by('month')
        chart_data_points = [
            {
                'x': d['month'].strftime('%Y-%m-%d'),
                'y': float(d['total_facturado'])
            }
            for d in data if d['total_facturado'] is not None
        ]
    
        year_str = self.kwargs.get('year')

        context['selected_year'] = int(year_str) if year_str else None        
        context['available_years'] = Factura.objects.dates('fecha_emision', 'year', order='DESC')
        context['chart_data'] = chart_data_points
        context['page_name'] = 'facutra_evolution'

        return context


class CalculoIvaTrimestralView(LoginRequiredMixin, TemplateView):
    template_name = 'backoffice/calculo_iva.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        selected_year = self.kwargs.get('year', date.today().year)

        if user.is_superuser:
            base_queryset = Factura.objects.all()
        else:
            try:
                base_queryset = Factura.objects.filter(proveedor=user.proveedor_profile)
            except AttributeError:
                base_queryset = Factura.objects.none()

        resultados = base_queryset.filter(
            fecha_emision__year=selected_year
        ).annotate(
            trimestre=Extract('fecha_emision', 'quarter')
        ).values(
            'trimestre'
        ).annotate(
            iva_total=Sum('importe_iva')
        ).order_by('trimestre')

        resultados_dict = {r['trimestre']: r['iva_total'] for r in resultados}
        
        context['resultados_trimestrales'] = [
            {'trimestre': 1, 'iva_a_pagar': resultados_dict.get(1, 0)},
            {'trimestre': 2, 'iva_a_pagar': resultados_dict.get(2, 0)},
            {'trimestre': 3, 'iva_a_pagar': resultados_dict.get(3, 0)},
            {'trimestre': 4, 'iva_a_pagar': resultados_dict.get(4, 0)},
        ]
        
        context['selected_year'] = selected_year
        context['available_years'] = base_queryset.dates('fecha_emision', 'year', order='DESC')
        context['titulo'] = f"Cálculo de IVA Trimestral - Año {selected_year}"
        context['page_name'] = 'iva_trimestal'
        
        return context