# backoffice/urls.py

from django.urls import path
from .views import FacturaListView, generar_pdf_factura

urlpatterns = [
    path('facturas/', FacturaListView.as_view(), name='factura_list'),
    path('facturas/<int:factura_id>/pdf/', generar_pdf_factura, name='factura_pdf'),
]