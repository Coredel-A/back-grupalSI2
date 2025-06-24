from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Bitacora
from .serializers import BitacoraSerializer

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class BitacoraViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bitacora.objects.all().order_by('-timestamp')
    serializer_class = BitacoraSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['usuario', 'ip', 'timestamp']
    search_fields = ['accion', 'usuario__email', 'usuario__nombre']
    ordering_fields = ['timestamp', 'usuario']

def exportar_bitacora_pdf(request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="bitacora.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        y = height - 50  # Margen superior

        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, y, "REPORTE DE BITÁCORA")
        y -= 30

        p.setFont("Helvetica", 10)

        bitacoras = Bitacora.objects.all().order_by('-timestamp')[:50]  # últimos 50 registros

        for b in bitacoras:
            linea = f"{b.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {b.usuario.nombre} {b.usuario.apellido} - {b.accion} - IP: {b.ip}"
            p.drawString(30, y, linea)
            y -= 15
            if y < 50:
                p.showPage()
                p.setFont("Helvetica", 10)
                y = height - 50

        p.showPage()
        p.save()
        return response


