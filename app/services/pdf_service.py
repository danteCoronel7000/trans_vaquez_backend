from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.schemas.reportes import ReporteServiciosResponse


def generar_pdf_reporte_servicios(reporte: ReporteServiciosResponse) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), topMargin=1.5*cm, bottomMargin=1.5*cm)

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=16, spaceAfter=6)
    subtitulo_style = ParagraphStyle('Subtitulo', parent=styles['Normal'], fontSize=9, textColor=colors.grey)

    elementos = []

    elementos.append(Paragraph("Reporte de Servicios de Transporte", titulo_style))

    periodo_texto = "Todos los registros"
    if reporte.filtro_aplicado.tipo_periodo == "fecha_especifica":
        periodo_texto = f"Fecha: {reporte.filtro_aplicado.fecha_inicio}"
    elif reporte.filtro_aplicado.tipo_periodo == "rango":
        periodo_texto = f"Del {reporte.filtro_aplicado.fecha_inicio} al {reporte.filtro_aplicado.fecha_fin}"

    elementos.append(Paragraph(f"{periodo_texto} — {reporte.total_filas} registros", subtitulo_style))
    elementos.append(Spacer(1, 0.5*cm))

    encabezados = [
        "ID", "Cliente", "Origen", "Destino", "Camión", "Chofer",
        "Fecha", "Estado", "Peso (kg)", "Vol. (m³)", "Costo (Bs.)",
        "Dist. (km)", "T. Est. (h)", "N° Clientes"
    ]

    datos = [encabezados]
    for f in reporte.filas:
        datos.append([
            str(f.id_servicio),
            f.cliente,
            f.origen[:30],
            f.destino[:30],
            f.camion,
            f.chofer,
            f.fecha.strftime('%d/%m/%Y'),
            f.estado,
            f"{f.peso_carga:.2f}",
            f"{f.volumen_carga:.2f}",
            f"{f.costo_cliente:.2f}",
            f"{f.distancia_ruta:.1f}" if f.distancia_ruta else "-",
            f"{f.tiempo_estimado_ruta:.1f}" if f.tiempo_estimado_ruta else "-",
            str(f.num_clientes_servicio),
        ])

    tabla = Table(datos, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    elementos.append(tabla)
    doc.build(elementos)

    buffer.seek(0)
    return buffer.read()