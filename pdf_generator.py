from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

# COMPRA PDF
def generate_compra_pdf(compra_data, buffer):
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()    
    story = []

    # --- CABECERA ---
    empresa_info = []
    if compra_data.get('empresa_logo_path'):
        img = Image(compra_data['empresa_logo_path'], width=1.2*inch, height=0.6*inch)
        img.hAlign = 'LEFT'
        empresa_info.append(img)
        empresa_info.append(Spacer(1, 8))
    empresa_info.append(Paragraph(compra_data.get('empresa_nombre', ''), styles['h4']))
    empresa_info.append(Paragraph(f"RNC: {compra_data.get('empresa_rnc', '')}", styles['Normal']))
    empresa_info.append(Paragraph(compra_data.get('empresa_direccion', ''), styles['Normal']))

    doc_info = [
        Paragraph("ORDEN DE COMPRA", styles['h2']),
        Paragraph(f"No. {compra_data['codigo']}", styles['Normal']),
        Paragraph(f"Fecha: {compra_data['fecha']}", styles['Normal']),
    ]

    header_table = Table([[empresa_info, doc_info]], colWidths=['70%', '30%'], style=[('VALIGN', (0, 0), (-1, -1), 'TOP')])
    story.append(header_table)
    story.append(Spacer(1, 24))

    # --- INFO PROVEEDOR ---
    proveedor_info = [
        Paragraph(f"<b>Proveedor:</b> {compra_data['proveedor_nombre']}", styles['Normal']),
        Paragraph(f"<b>RNC:</b> {compra_data['proveedor_rnc']}", styles['Normal']),
        Paragraph(f"<b>Condición:</b> {compra_data['condicion']}", styles['Normal']),
    ]
    story.extend(proveedor_info)
    story.append(Spacer(1, 12))

    # Detalles de la compra
    data = [['Código', 'Descripción', 'Cantidad', 'Precio Unitario', 'Importe']]
    for item in compra_data['detalles']:
        data.append([
            item['mercancia_codigo'],
            item['mercancia_nombre'],
            str(item['cantidad']),
            f"{item['precio']:.2f}",
            f"{item['importe']:.2f}"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # Totales
    story.append(Paragraph(f"Subtotal: {compra_data['subtotal']:.2f}", styles['Normal']))
    story.append(Paragraph(f"Descuento: {compra_data['descuento']:.2f}", styles['Normal']))
    story.append(Paragraph(f"ITBIS (18%): {compra_data['itbis']:.2f}", styles['Normal']))
    story.append(Paragraph(f"Total: {compra_data['total']:.2f}", styles['h3']))

    doc.build(story)


# FACTURA PDF

def generate_invoice_pdf(invoice_data, buffer):
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()    
    story = []

    # --- CABECERA ---
    empresa_info = []
    if invoice_data.get('empresa_logo_path'):
        img = Image(invoice_data['empresa_logo_path'], width=1.2*inch, height=0.6*inch)
        img.hAlign = 'LEFT'
        empresa_info.append(img)
        empresa_info.append(Spacer(1, 8))
    empresa_info.append(Paragraph(invoice_data.get('empresa_nombre', ''), styles['h4']))
    empresa_info.append(Paragraph(f"RNC: {invoice_data.get('empresa_rnc', '')}", styles['Normal']))
    empresa_info.append(Paragraph(invoice_data.get('empresa_direccion', ''), styles['Normal']))

    doc_info = [
        Paragraph("FACTURA", styles['h2']),
        Paragraph(f"No. {invoice_data['codigo']}", styles['Normal']),
        Paragraph(f"Fecha: {invoice_data['fecha']}", styles['Normal']),
    ]

    header_table = Table([[empresa_info, doc_info]], colWidths=['70%', '30%'], style=[('VALIGN', (0, 0), (-1, -1), 'TOP')])
    story.append(header_table)
    story.append(Spacer(1, 24))

    # --- INFO CLIENTE ---
    cliente_info = [
        Paragraph(f"<b>Cliente:</b> {invoice_data['cliente_nombre']}", styles['Normal']),
        Paragraph(f"<b>RNC:</b> {invoice_data['cliente_rnc']}", styles['Normal']),
        Paragraph(f"<b>Condición:</b> {invoice_data['condicion']}", styles['Normal']),
    ]
    story.extend(cliente_info)
    story.append(Spacer(1, 12))

    # Detalles de la factura
    data = [['Código', 'Descripción', 'Cantidad', 'Precio Unitario', 'Importe']]
    for item in invoice_data['detalles']:
        data.append([
            item['mercancia_codigo'],
            item['mercancia_nombre'],
            str(item['cantidad']),
            f"{item['precio']:.2f}",
            f"{item['importe']:.2f}"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # Totales
    story.append(Paragraph(f"Subtotal: {invoice_data['subtotal']:.2f}", styles['Normal']))
    story.append(Paragraph(f"Descuento: {invoice_data['descuento']:.2f}", styles['Normal']))
    story.append(Paragraph(f"ITBIS (18%): {invoice_data['itbis']:.2f}", styles['Normal']))
    story.append(Paragraph(f"Total: {invoice_data['total']:.2f}", styles['h3']))

    doc.build(story)

# RECIBO DE COBRO PDF
def generate_cobro_pdf(cobro_data, buffer):
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()    
    story = []

    # --- CABECERA ---
    empresa_info = []
    if cobro_data.get('empresa_logo_path'):
        img = Image(cobro_data['empresa_logo_path'], width=1.2*inch, height=0.6*inch)
        img.hAlign = 'LEFT'
        empresa_info.append(img)
        empresa_info.append(Spacer(1, 8))
    empresa_info.append(Paragraph(cobro_data.get('empresa_nombre', ''), styles['h4']))
    empresa_info.append(Paragraph(f"RNC: {cobro_data.get('empresa_rnc', '')}", styles['Normal']))
    empresa_info.append(Paragraph(cobro_data.get('empresa_direccion', ''), styles['Normal']))

    doc_info = [
        Paragraph("RECIBO DE COBRO", styles['h2']),
        Paragraph(f"No. {cobro_data['codigo']}", styles['Normal']),
        Paragraph(f"Fecha: {cobro_data['fecha']}", styles['Normal']),
    ]

    header_table = Table([[empresa_info, doc_info]], colWidths=['70%', '30%'], style=[('VALIGN', (0, 0), (-1, -1), 'TOP')])
    story.append(header_table)
    story.append(Spacer(1, 24))

    # --- INFO CLIENTE ---
    cliente_info = [
        Paragraph(f"<b>Recibido de:</b> {cobro_data['cliente_nombre']}", styles['Normal']),
        Paragraph(f"<b>RNC:</b> {cobro_data['cliente_rnc']}", styles['Normal']),
        Paragraph(f"<b>Forma de Cobro:</b> {cobro_data.get('forma_pago', 'N/A')}", styles['Normal']),
    ]
    story.extend(cliente_info)
    story.append(Spacer(1, 12))

    # Detalles del cobro
    data = [['Factura Afectada', 'Monto Aplicado', 'Descuento', 'Cargo']]
    for item in cobro_data['detalles']:
        data.append([
            item['factura_codigo'],
            f"{item['aplicado']:.2f}",
            f"{item['descuento']:.2f}",
            f"{item['cargo']:.2f}",
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # Totales
    story.append(Paragraph(f"Total Recibido: {cobro_data['total']:.2f}", styles['h3']))

    doc.build(story)

def generate_pago_pdf(pago_data, buffer):
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()    
    story = []

    # --- CABECERA ---
    empresa_info = []
    if pago_data.get('empresa_logo_path'):
        img = Image(pago_data['empresa_logo_path'], width=1.2*inch, height=0.6*inch)
        img.hAlign = 'LEFT'
        empresa_info.append(img)
        empresa_info.append(Spacer(1, 8))
    empresa_info.append(Paragraph(pago_data.get('empresa_nombre', ''), styles['h4']))
    empresa_info.append(Paragraph(f"RNC: {pago_data.get('empresa_rnc', '')}", styles['Normal']))
    empresa_info.append(Paragraph(pago_data.get('empresa_direccion', ''), styles['Normal']))

    doc_info = [
        Paragraph("RECIBO DE PAGO", styles['h2']),
        Paragraph(f"No. {pago_data['codigo']}", styles['Normal']),
        Paragraph(f"Fecha: {pago_data['fecha']}", styles['Normal']),
    ]

    header_table = Table([[empresa_info, doc_info]], colWidths=['70%', '30%'], style=[('VALIGN', (0, 0), (-1, -1), 'TOP')])
    story.append(header_table)
    story.append(Spacer(1, 24))

    # --- INFO PROVEEDOR ---
    proveedor_info = [
        Paragraph(f"<b>Pagado a:</b> {pago_data['proveedor_nombre']}", styles['Normal']),
        Paragraph(f"<b>RNC:</b> {pago_data['proveedor_rnc']}", styles['Normal']),
        Paragraph(f"<b>Forma de Pago:</b> {pago_data.get('forma_pago', 'N/A')}", styles['Normal']),
    ]
    story.extend(proveedor_info)
    story.append(Spacer(1, 12))

    # Detalles del pago
    data = [['Compra Afectada', 'Monto Aplicado', 'Descuento', 'Cargo']]
    for item in pago_data['detalles']:
        data.append([
            item['compra_codigo'],
            f"{item['aplicado']:.2f}",
            f"{item['descuento']:.2f}",
            f"{item['cargo']:.2f}",
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # Totales
    story.append(Paragraph(f"Total Pagado: {pago_data['total']:.2f}", styles['h3']))

    doc.build(story)

def generate_purchase_pdf(purchase_data, buffer):
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título
    story.append(Paragraph("Compra", styles['h1']))
    story.append(Spacer(1, 0.2 * inch))

    # Información de la compra
    story.append(Paragraph(f"Código de Compra: {purchase_data['codigo']}", styles['Normal']))
    story.append(Paragraph(f"Fecha: {purchase_data['fecha']}", styles['Normal']))
    story.append(Paragraph(f"Proveedor: {purchase_data['proveedor_nombre']}", styles['Normal']))
    story.append(Paragraph(f"RNC Proveedor: {purchase_data['proveedor_rnc']}", styles['Normal']))
    story.append(Paragraph(f"Condición: {purchase_data['condicion']}", styles['Normal']))
    story.append(Paragraph(f"Comentario: {purchase_data['observaciones']}", styles['Normal']))
    story.append(Spacer(1, 0.2 * inch))

    # Detalles de la compra
    data = [['Código', 'Descripción', 'Cantidad', 'Precio Unitario', 'Importe']]
    for item in purchase_data['detalles']:
        data.append([
            item['mercancia_codigo'],
            item['mercancia_nombre'],
            str(item['cantidad']),
            f"{item['precio']:.2f}",
            f"{item['importe']:.2f}"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # Totales
    story.append(Paragraph(f"Subtotal: {purchase_data['subtotal']:.2f}", styles['Normal']))
    story.append(Paragraph(f"Descuento: {purchase_data['descuento']:.2f}", styles['Normal']))
    story.append(Paragraph(f"ITBIS (18%): {purchase_data['itbis']:.2f}", styles['Normal']))
    story.append(Paragraph(f"Total: {purchase_data['total']:.2f}", styles['h3']))

    doc.build(story)

# DEVOLUCION PDF
def generate_devolucion_pdf(devolucion_data, buffer):
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()    
    story = []

    # --- CABECERA ---
    title = "Nota de Crédito (Devolución de Venta)" if devolucion_data['tipo'] == 'venta' else "Nota de Débito (Devolución de Compra)"
    empresa_info = []
    if devolucion_data.get('empresa_logo_path'):
        img = Image(devolucion_data['empresa_logo_path'], width=1.2*inch, height=0.6*inch)
        img.hAlign = 'LEFT'
        empresa_info.append(img)
        empresa_info.append(Spacer(1, 8))
    empresa_info.append(Paragraph(devolucion_data.get('empresa_nombre', ''), styles['h4']))
    empresa_info.append(Paragraph(f"RNC: {devolucion_data.get('empresa_rnc', '')}", styles['Normal']))
    empresa_info.append(Paragraph(devolucion_data.get('empresa_direccion', ''), styles['Normal']))

    doc_info = [
        Paragraph(title.upper(), styles['h2']),
        Paragraph(f"No. {devolucion_data['codigo']}", styles['Normal']),
        Paragraph(f"Fecha: {devolucion_data['fecha']}", styles['Normal']),
    ]

    header_table = Table([[empresa_info, doc_info]], colWidths=['70%', '30%'], style=[('VALIGN', (0, 0), (-1, -1), 'TOP')])
    story.append(header_table)
    story.append(Spacer(1, 24))

    # --- INFO CLIENTE/PROVEEDOR ---
    if devolucion_data['tipo'] == 'venta':
        story.append(Paragraph(f"<b>Cliente:</b> {devolucion_data.get('cliente_nombre', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>RNC:</b> {devolucion_data.get('cliente_rnc', 'N/A')}", styles['Normal']))
    else:
        story.append(Paragraph(f"<b>Proveedor:</b> {devolucion_data.get('proveedor_nombre', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>RNC:</b> {devolucion_data.get('proveedor_rnc', 'N/A')}", styles['Normal']))

    story.append(Spacer(1, 12))

    # Detalles de la devolución
    data = [['Documento Origen', 'Código', 'Descripción', 'Cantidad', 'Precio', 'Importe']]
    for item in devolucion_data['detalles']:
        data.append([
            item['documento_origen_codigo'],
            item['mercancia_codigo'],
            item['mercancia_nombre'],
            str(item['cantidad']),
            f"{item['precio']:.2f}",
            f"{item['importe']:.2f}"
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # Totales
    story.append(Paragraph(f"Subtotal: {devolucion_data['subtotal']:.2f}", styles['Normal']))
    story.append(Paragraph(f"ITBIS (18%): {devolucion_data['itbis']:.2f}", styles['Normal']))
    story.append(Paragraph(f"Total: {devolucion_data['total']:.2f}", styles['h3']))

    doc.build(story)


def generate_cobros_report_pdf(cobros, buffer, desde, hasta):
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph('Reporte de Cobros por Fecha', styles['Title']))
    elements.append(Paragraph(f"Rango de fechas: {desde} a {hasta}", styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [['Código', 'Fecha', 'Cliente', 'Forma de Pago', 'Total']]
    total_general = 0.0

    for cobro in cobros:
        total_general += float(cobro.total or 0.0)
        data.append([
            cobro.codigo or '',
            cobro.fecha.strftime('%d/%m/%Y') if cobro.fecha else '',
            cobro.cliente.nombre if cobro.cliente else 'N/A',
            cobro.forma_pago or '',
            f"{float(cobro.total or 0.0):,.2f}"
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (4,1), (4,-1), 'RIGHT'), # Alinear total a la derecha
        ('GRID', (0,0), (-1,-1), 0.5, colors.gray),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Total General: {total_general:,.2f}", styles['Heading3']))

    doc.build(elements)


def generate_pagos_report_pdf(pagos, buffer, desde, hasta):
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph('Reporte de Pagos por Fecha', styles['Title']))
    elements.append(Paragraph(f"Rango de fechas: {desde} a {hasta}", styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [['Código', 'Fecha', 'Proveedor', 'Forma de Pago', 'Total']]
    total_general = 0.0

    for pago in pagos:
        total_general += float(pago.total or 0.0)
        data.append([
            pago.codigo or '',
            pago.fecha.strftime('%d/%m/%Y') if pago.fecha else '',
            pago.proveedor.nombre if pago.proveedor else 'N/A',
            pago.forma_pago or '',
            f"{float(pago.total or 0.0):,.2f}"
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (4,1), (4,-1), 'RIGHT'), # Alinear total a la derecha
        ('GRID', (0,0), (-1,-1), 0.5, colors.gray),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Total General: {total_general:,.2f}", styles['Heading3']))

    doc.build(elements)



    