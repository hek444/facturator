# backoffice/urls.py

from django.urls import path
from .views import FacturaListView, generar_pdf_factura, login_redirect_view, FacturacionEvolucionView, FacturaDetailView, CalculoIvaTrimestralView

app_name = 'backoffice'

urlpatterns = [
    path('factura/<int:pk>/', FacturaDetailView.as_view(), name='factura_detail'),
    path('facturas/<int:year>/<int:quarter>/', FacturaListView.as_view(), name='factura_list_by_quarter'),
    path('facturas/', FacturaListView.as_view(), name='factura_list'),
    path('facturas/<int:year>/', FacturaListView.as_view(), name='factura_list_by_year'),
    path('evolucion/', FacturacionEvolucionView.as_view(), name='facturacion_evolucion'),
    path('evolucion/<int:year>/', FacturacionEvolucionView.as_view(), name='facturacion_evolucion_by_year'),
    path('iva/', CalculoIvaTrimestralView.as_view(), name='calculo_iva'),
    path('iva/<int:year>/', CalculoIvaTrimestralView.as_view(), name='calculo_iva_por_ano'),
    
    path('facturas/<int:factura_id>/pdf/', generar_pdf_factura, name='factura_pdf'),
    path('redirect/', login_redirect_view, name='login_redirect_handler'),
]