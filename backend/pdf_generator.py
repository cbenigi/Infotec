from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from models import Visita, Zona, Cliente, User, Empresa
from datetime import datetime
import os

def generate_pdf(visita_id):
    visita = Visita.query.get(visita_id)
    if not visita:
        return None

    # Validar al menos una foto
    zonas = Zona.query.filter_by(visita_id=visita_id).all()
    has_photo = any(z.foto_url for z in zonas)
    if not has_photo:
        return None

    # Obtener datos de la empresa del usuario
    empresa = Empresa.query.filter_by(user_id=visita.supervisor_id).first()
    if not empresa:
        # Intentar con el técnico si el supervisor no tiene empresa
        empresa = Empresa.query.filter_by(user_id=visita.tecnico_id).first()
    
    # Usar datos de la empresa o valores por defecto
    empresa_nombre = empresa.nombre if empresa else "Empresa"
    empresa_telefono = empresa.telefono if empresa else "N/A"
    empresa_direccion = empresa.direccion if empresa else "N/A"
    empresa_correo = empresa.correo if empresa else "N/A"

    filename = f"informe_{visita_id}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Header con logo
    if empresa and empresa.logo_url:
        # Usar el logo de la empresa si existe
        logo_path = os.path.join('uploads', empresa.logo_url.split('/')[-1])
        if os.path.exists(logo_path):
            logo = Image(logo_path, 1*inch, 1*inch)
            elements.append(logo)
    else:
        # Placeholder logo: círculo verde con texto
        from reportlab.lib.colors import Color
        from reportlab.pdfgen import canvas
        c = canvas.Canvas("temp_logo.pdf")
        c.setFillColor(Color(0, 128/255, 0))  # Verde
        c.circle(50, 50, 40, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(50, 45, empresa_nombre[:3].upper())
        c.save()
        logo = Image("temp_logo.pdf", 1*inch, 1*inch)
        elements.append(logo)

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, textColor=colors.lightblue, alignment=1)
    elements.append(Paragraph("INFORME PRESTACIÓN DEL SERVICIO", title_style))
    elements.append(Spacer(1, 0.2*inch))

    # Tabla Datos Iniciales
    data = [
        ['Cliente', visita.cliente.nombre, 'NIT', visita.cliente.nit],
        ['Administrador', visita.cliente.administrador, 'Correo', visita.cliente.correo],
        ['Código', visita.cliente.tipo_codigo, 'Fecha Visita Técnica', visita.fecha.strftime('%d/%m/%Y')],
        ['Supervisor', visita.supervisor.nombre, 'ID Visita Técnica', visita.id],
        ['Goal', str(visita.goal), 'Calificación', str(visita.calificacion)]
    ]
    table = Table(data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.green),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))

    # Secciones Zonas
    for zona in zonas:
        elements.append(Paragraph(f"<b>{zona.nombre}</b>", styles['Heading2']))
        zona_data = [
            ['Observaciones', zona.observaciones],
            ['Actividades', zona.actividades],
            ['Calificación', zona.calificacion]
        ]
        zona_table = Table(zona_data, colWidths=[1.5*inch, 4*inch])
        zona_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.green),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        elements.append(zona_table)
        if zona.foto_url:
            img_path = os.path.join('uploads', zona.foto_url.split('/')[-1])
            if os.path.exists(img_path):
                img = Image(img_path, 2*inch, 2*inch)
                elements.append(img)
        elements.append(Spacer(1, 0.3*inch))

    # Sección Seguridad
    elements.append(Paragraph("<b>Seguridad y salud en el trabajo</b>", ParagraphStyle('Section', parent=styles['Heading2'], background=colors.lightcoral)))
    if visita.seguridad_obs:
        elements.append(Paragraph(visita.seguridad_obs, styles['Normal']))
    # Aquí agregar subcomponentes con fotos si aplica

    # Sección Productividad
    elements.append(Paragraph("<b>Productividad</b>", ParagraphStyle('Section', parent=styles['Heading2'], background=colors.lightpurple)))
    if visita.productividad_obs:
        elements.append(Paragraph(visita.productividad_obs, styles['Normal']))

    # Sección Conclusiones
    elements.append(Paragraph("<b>Conclusiones</b>", ParagraphStyle('Section', parent=styles['Heading2'], background=colors.lightgreen)))
    if visita.conclusiones_obs:
        elements.append(Paragraph(visita.conclusiones_obs, styles['Normal']))

    # Footer
    elements.append(Spacer(1, 1*inch))
    footer_text = f"{empresa_nombre} - {empresa_direccion} - Tel: {empresa_telefono} - Email: {empresa_correo} - Fecha: {datetime.now().strftime('%d/%m/%Y')}"
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', alignment=1, fontSize=10)))

    doc.build(elements)
    return filename