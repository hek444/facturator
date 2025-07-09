# backoffice/urls.py

from django.urls import path
from .views import FacturaListView, generar_pdf_factura, login_redirect_view, FacturacionEvolucionView

app_name = 'backoffice'

urlpatterns = [
    path('facturas/', FacturaListView.as_view(), name='factura_list'),
    path('facturas/<int:year>/', FacturaListView.as_view(), name='factura_list_by_year'),
    path('evolucion/', FacturacionEvolucionView.as_view(), name='facturacion_evolucion'),
    path('evolucion/<int:year>/', FacturacionEvolucionView.as_view(), name='facturacion_evolucion_by_year'),


    path('facturas/<int:factura_id>/pdf/', generar_pdf_factura, name='factura_pdf'),
    path('redirect/', login_redirect_view, name='login_redirect_handler'),
]