from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.schemas.reportes import ReporteServiciosResponse
from reportlab.platypus import KeepTogether
from app.schemas.reportes import ReporteServiciosPorClienteResponse
from app.schemas.reportes import ReporteViajesPorChoferResponse


def _tabla_resumen_chofer(resumen) -> Table:
    tabla = Table([
        ["Prog.", "En curso", "Final.", "Cancel.", "Km", "Horas est.", "Peso (kg)",
         "Ingresos (Bs.)", "C. Operat. (Bs.)", "Viáticos chofer (Bs.)", "Utilidad (Bs.)"],
        [str(resumen.viajes_programados), str(resumen.viajes_en_curso),
         str(resumen.viajes_finalizados), str(resumen.viajes_cancelados),
         _fmt(resumen.km_total, 1), _fmt(resumen.horas_estimadas_total, 1),
         _fmt(resumen.peso_total), _fmt(resumen.ingresos_total),
         _fmt(resumen.costo_operativo_total), _fmt(resumen.viaticos_chofer_total),
         _fmt(resumen.utilidad_total)],
    ], hAlign='LEFT')
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return tabla


def generar_pdf_reporte_viajes_por_chofer(reporte: ReporteViajesPorChoferResponse) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(letter),
        leftMargin=1*cm, rightMargin=1*cm, topMargin=1.2*cm, bottomMargin=1.2*cm,
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=16, spaceAfter=4)
    sub_style    = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
    grupo_style  = ParagraphStyle('Grupo', parent=styles['Heading3'], fontSize=10,
                                  spaceBefore=10, spaceAfter=4, keepWithNext=1)
    cell_style   = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=6, leading=7)
    nota_style   = ParagraphStyle('Nota', parent=styles['Normal'], fontSize=7, textColor=colors.grey)

    elementos = [
        Paragraph("Reporte de Viajes por Chofer", titulo_style),
        Paragraph(
            f"{_periodo_texto(reporte.filtro_aplicado)} — {reporte.total_choferes} choferes",
            sub_style,
        ),
        Paragraph(
            "Los viajes cancelados se listan pero no se incluyen en los totales. "
            "La duración real solo se calcula en viajes con al menos 2 puntos GPS.",
            nota_style,
        ),
        Spacer(1, 0.3*cm),
    ]

    encabezados = [
        "Fecha", "Ruta", "Origen", "Destino", "Camión", "Estado", "N° Cli.",
        "Peso (kg)", "Vol. (m³)", "Ingresos (Bs.)", "C. Operat. (Bs.)", "Utilidad (Bs.)",
        "% Peso cam.", "Bs/km oper.", "Vel. est. (km/h)", "Durac. real (h)",
    ]
    col_widths = [40, 52, 56, 56, 56, 38, 24, 36, 32, 42, 42, 40, 32, 32, 32, 34]

    for grupo in reporte.grupos:
        titulo_grupo = f"{grupo.chofer}  —  Lic. {grupo.licencia or 'sin registrar'}"
        if grupo.categoria:
            titulo_grupo += f"  (Cat. {grupo.categoria})"
        elementos.append(Paragraph(titulo_grupo, grupo_style))

        datos = [encabezados]
        estilos_extra = []

        for i, f in enumerate(grupo.filas, start=1):
            datos.append([
                f.fecha.strftime('%d/%m/%Y'),
                Paragraph(f.ruta, cell_style),
                Paragraph(f.origen, cell_style),
                Paragraph(f.destino, cell_style),
                Paragraph(f.camion, cell_style),
                f.estado,
                str(f.num_clientes),
                _fmt(f.peso_transportado), _fmt(f.volumen_transportado),
                _fmt(f.ingresos_viaje), _fmt(f.costo_operativo), _fmt(f.utilidad_viaje),
                _fmt(f.ocupacion_peso_pct, 1), _fmt(f.costo_operativo_por_km),
                _fmt(f.velocidad_promedio_estimada, 1), _fmt(f.duracion_real_horas),
            ])
            if f.utilidad_viaje < 0:
                estilos_extra.append(('TEXTCOLOR', (11, i), (11, i), colors.HexColor('#dc2626')))

        tabla = Table(datos, colWidths=col_widths, repeatRows=1)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            *estilos_extra,
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 0.15*cm))
        elementos.append(KeepTogether([_tabla_resumen_chofer(grupo.resumen)]))

    elementos.append(Spacer(1, 0.5*cm))
    elementos.append(Paragraph("Resumen general", grupo_style))
    elementos.append(_tabla_resumen_chofer(reporte.resumen_general))

    doc.build(elementos)
    buffer.seek(0)
    return buffer.read()

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

def _fmt(valor, decimales: int = 2) -> str:
    return "—" if valor is None else f"{valor:.{decimales}f}"


def _periodo_texto(filtro) -> str:
    if filtro.tipo_periodo == "fecha_especifica":
        return f"Fecha: {filtro.fecha_inicio}"
    if filtro.tipo_periodo == "rango":
        return f"Del {filtro.fecha_inicio} al {filtro.fecha_fin}"
    return "Todos los registros"


def _tabla_resumen(resumen) -> Table:
    tabla = Table([
        ["Servicios", "Peso (kg)", "Volumen (m³)", "Facturado (Bs.)",
         "C. Operativo (Bs.)", "Utilidad (Bs.)", "Bs/kg prom."],
        [str(resumen.total_servicios), _fmt(resumen.peso_total), _fmt(resumen.volumen_total),
         _fmt(resumen.costo_total), _fmt(resumen.costo_operativo_total),
         _fmt(resumen.utilidad_total), _fmt(resumen.costo_promedio_por_kg)],
    ], hAlign='LEFT')
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return tabla


def generar_pdf_reporte_servicios_por_cliente(reporte: ReporteServiciosPorClienteResponse) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(letter),
        leftMargin=1*cm, rightMargin=1*cm, topMargin=1.2*cm, bottomMargin=1.2*cm,
    )

    styles = getSampleStyleSheet()
    titulo_style  = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=16, spaceAfter=4)
    sub_style     = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
    cliente_style = ParagraphStyle('Cliente', parent=styles['Heading3'], fontSize=10,
                                   spaceBefore=10, spaceAfter=4, keepWithNext=1)
    cell_style    = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=6, leading=7)
    nota_style    = ParagraphStyle('Nota', parent=styles['Normal'], fontSize=7, textColor=colors.grey)

    elementos = [
        Paragraph("Reporte de Servicios por Cliente", titulo_style),
        Paragraph(
            f"{_periodo_texto(reporte.filtro_aplicado)} — {reporte.total_clientes} clientes",
            sub_style,
        ),
        Paragraph(
            "Los servicios cancelados se listan pero no se incluyen en los totales.",
            nota_style,
        ),
        Spacer(1, 0.3*cm),
    ]

    encabezados = [
        "Fecha", "Origen", "Destino", "Camión", "Chofer", "Estado",
        "Peso (kg)", "Vol. (m³)", "Costo (Bs.)", "Bs/kg", "Bs/m³",
        "% Peso cam.", "% Vol. cam.", "% Partic.", "C. Operat. (Bs.)", "Utilidad (Bs.)",
    ]
    col_widths = [40, 62, 62, 58, 58, 40, 36, 32, 40, 32, 34, 34, 34, 34, 40, 40]

    for grupo in reporte.grupos:
        titulo_grupo = grupo.cliente
        if grupo.razon_social:
            titulo_grupo += f"  —  {grupo.razon_social}"
        if grupo.nit:
            titulo_grupo += f"  (NIT {grupo.nit})"
        elementos.append(Paragraph(titulo_grupo, cliente_style))

        datos = [encabezados]
        estilos_extra = []

        for i, f in enumerate(grupo.filas, start=1):
            datos.append([
                f.fecha.strftime('%d/%m/%Y'),
                Paragraph(f.origen, cell_style),
                Paragraph(f.destino, cell_style),
                Paragraph(f.camion, cell_style),
                Paragraph(f.chofer, cell_style),
                f.estado,
                _fmt(f.peso_carga), _fmt(f.volumen_carga), _fmt(f.costo_cliente),
                _fmt(f.costo_por_kg), _fmt(f.costo_por_m3),
                _fmt(f.ocupacion_peso_pct, 1), _fmt(f.ocupacion_volumen_pct, 1),
                _fmt(f.participacion_pct, 1),
                _fmt(f.costo_operativo_prorrateado), _fmt(f.utilidad_estimada),
            ])
            if f.utilidad_estimada < 0:
                estilos_extra.append(('TEXTCOLOR', (15, i), (15, i), colors.HexColor('#dc2626')))

        tabla = Table(datos, colWidths=col_widths, repeatRows=1)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('FONTSIZE', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            *estilos_extra,
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 0.15*cm))
        elementos.append(KeepTogether([_tabla_resumen(grupo.resumen)]))

    elementos.append(Spacer(1, 0.5*cm))
    elementos.append(Paragraph("Resumen general", cliente_style))
    elementos.append(_tabla_resumen(reporte.resumen_general))

    doc.build(elementos)
    buffer.seek(0)
    return buffer.read()