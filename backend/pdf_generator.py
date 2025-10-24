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

    # Obtener zonas de la visita
    zonas = Zona.query.filter_by(visita_id=visita_id).all()
    if not zonas:
        return None

    # Obtener datos de la empresa del usuario
    empresa = Empresa.query.filter_by(user_id=visita.supervisor_id).first()
    
    # Usar datos de la empresa o valores por defecto
    empresa_nombre = empresa.nombre if empresa else "Empresa"
    empresa_telefono = empresa.telefono if empresa else "N/A"
    empresa_direccion = empresa.direccion if empresa else "N/A"
    empresa_correo = empresa.correo if empresa else "N/A"

    filename = f"informe_{visita_id}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Header con logos (empresa y cliente)
    header_elements = []
    
    # Logo de la empresa
    if empresa and empresa.logo_url:
        # Usar el logo de la empresa si existe
        logo_path = os.path.join('uploads', empresa.logo_url.split('/')[-1])
        if os.path.exists(logo_path):
            try:
                # Verificar que el archivo sea una imagen válida
                from PIL import Image as PILImage
                with PILImage.open(logo_path) as img:
                    img.verify()  # Verificar que sea una imagen válida
                
                empresa_logo = Image(logo_path, 1*inch, 1*inch)
                header_elements.append(empresa_logo)
            except Exception as e:
                print(f"Error cargando logo de empresa {logo_path}: {str(e)}")
                empresa_texto = Paragraph(f"<b>{empresa_nombre[:3].upper()}</b>", styles['Heading3'])
                header_elements.append(empresa_texto)
    else:
        # Placeholder logo de empresa: texto simple
        empresa_texto = Paragraph(f"<b>{empresa_nombre[:3].upper()}</b>", styles['Heading3'])
        header_elements.append(empresa_texto)
    
    # Logo del cliente
    if visita.cliente.logo_url:
        cliente_logo_path = os.path.join('uploads', visita.cliente.logo_url.split('/')[-1])
        if os.path.exists(cliente_logo_path):
            try:
                # Verificar que el archivo sea una imagen válida
                from PIL import Image as PILImage
                with PILImage.open(cliente_logo_path) as img:
                    img.verify()  # Verificar que sea una imagen válida
                
                cliente_logo = Image(cliente_logo_path, 1*inch, 1*inch)
                header_elements.append(cliente_logo)
            except Exception as e:
                print(f"Error cargando logo de cliente {cliente_logo_path}: {str(e)}")
                # No agregar nada si falla el logo del cliente
    
    # Agregar logos al documento
    if header_elements:
        # Crear tabla para alinear logos horizontalmente
        logo_table = Table([header_elements], colWidths=[len(header_elements) * 1*inch])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(logo_table)

    # Título principal con estilo profesional
    title_style = ParagraphStyle(
        'Title', 
        parent=styles['Heading1'], 
        fontSize=16, 
        textColor=colors.darkblue, 
        alignment=1,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    elements.append(Paragraph("INFORME PRESTACIÓN DEL SERVICIO", title_style))
    elements.append(Spacer(1, 0.3*inch))

    # Tabla Datos Iniciales
    data = [
        ['Cliente', visita.cliente.nombre, 'NIT', visita.cliente.nit],
        ['Administrador', visita.cliente.administrador, 'Correo', visita.cliente.correo],
        ['Código', visita.cliente.tipo_codigo, 'Fecha Visita Técnica', visita.fecha.strftime('%d/%m/%Y')],
        ['Supervisor', visita.supervisor.nombre, 'ID Visita Técnica', visita.id]
    ]
    table = Table(data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),  # Header azul profesional
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),      # Texto blanco en header
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.darkblue),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),  # Filas alternadas
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))

    # Agrupar zonas por sección
    secciones = {}
    for zona in zonas:
        if zona.seccion not in secciones:
            secciones[zona.seccion] = []
        secciones[zona.seccion].append(zona)

    # Renderizar cada sección
    for seccion_nombre, zonas_seccion in secciones.items():
        elements.append(Spacer(1, 0.3*inch))
        # Títulos de sección con colores profesionales
        seccion_colors = {
            'Aseo y Limpieza': colors.darkgreen,
            'Seguridad y Salud': colors.darkred,
            'Colaborador': colors.darkorange
        }
        color = seccion_colors.get(seccion_nombre, colors.darkblue)
        
        seccion_style = ParagraphStyle(
            'Seccion',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=color,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            spaceBefore=12
        )
        elements.append(Paragraph(f"SECCIÓN: {seccion_nombre.upper()}", seccion_style))
        
        # Crear tabla de dos columnas para las actividades
        actividades_data = []
        for i in range(0, len(zonas_seccion), 2):
            row = []
            for j in range(2):
                if i + j < len(zonas_seccion):
                    zona = zonas_seccion[i + j]
                    actividad_text = f"""
                    <b>Concepto Actividad:</b> {zona.concepto_actividad}<br/>
                    <b>Calificación:</b> {zona.calificacion}<br/>
                    <b>Observaciones:</b> {zona.observaciones or 'Sin observaciones'}
                    """
                    row.append(actividad_text)
                else:
                    row.append("")
            actividades_data.append(row)
        
        if actividades_data:
            actividades_table = Table(actividades_data, colWidths=[3*inch, 3*inch])
            actividades_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightgrey]),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(actividades_table)
        
        # Agregar fotos de evidencia (solo para Aseo y Seguridad)
        if seccion_nombre in ['Aseo y Limpieza', 'Seguridad y Salud']:
            fotos_data = []
            for zona in zonas_seccion:
                if zona.foto_url:
                    foto_path = os.path.join('uploads', zona.foto_url.split('/')[-1])
                    if os.path.exists(foto_path):
                        try:
                            # Verificar que el archivo sea una imagen válida
                            from PIL import Image as PILImage
                            with PILImage.open(foto_path) as img:
                                img.verify()  # Verificar que sea una imagen válida
                            
                            foto = Image(foto_path, 2*inch, 2*inch)
                            fotos_data.append(foto)
                        except Exception as e:
                            print(f"Error cargando imagen {foto_path}: {str(e)}")
                            fotos_data.append(Paragraph(f"Error cargando imagen: {os.path.basename(foto_path)}", styles['Normal']))
            
            if fotos_data:
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph("EVIDENCIA FOTOGRÁFICA:", styles['Heading3']))
                # Crear tabla de fotos en dos columnas
                fotos_table_data = []
                for i in range(0, len(fotos_data), 2):
                    row = []
                    for j in range(2):
                        if i + j < len(fotos_data):
                            row.append(fotos_data[i + j])
                        else:
                            row.append("")
                    fotos_table_data.append(row)
                
                if fotos_table_data:
                    fotos_table = Table(fotos_table_data, colWidths=[2.5*inch, 2.5*inch])
                    fotos_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    elements.append(fotos_table)

    # Sección Conclusiones con estilo profesional
    if visita.conclusiones:
        elements.append(Spacer(1, 0.4*inch))
        
        # Título de conclusiones con fondo
        conclusiones_style = ParagraphStyle(
            'Conclusiones',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            backColor=colors.darkblue,
            spaceAfter=8,
            spaceBefore=8,
            alignment=1,
            borderPadding=8
        )
        elements.append(Paragraph("CONCLUSIONES", conclusiones_style))
        
        # Texto de conclusiones con estilo
        conclusiones_text_style = ParagraphStyle(
            'ConclusionesText',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            fontName='Helvetica',
            spaceAfter=6,
            leftIndent=20,
            rightIndent=20,
            borderWidth=1,
            borderColor=colors.lightblue,
            borderPadding=10,
            backColor=colors.lightgrey
        )
        elements.append(Paragraph(visita.conclusiones, conclusiones_text_style))

    # Footer profesional
    elements.append(Spacer(1, 1*inch))
    footer_style = ParagraphStyle(
        'Footer',
        alignment=1,
        fontSize=9,
        textColor=colors.darkgrey,
        fontName='Helvetica',
        backColor=colors.lightgrey,
        borderWidth=1,
        borderColor=colors.grey,
        borderPadding=6,
        spaceBefore=12
    )
    footer_text = f"{empresa_nombre} | {empresa_direccion} | Tel: {empresa_telefono} | Email: {empresa_correo} | Fecha: {datetime.now().strftime('%d/%m/%Y')}"
    elements.append(Paragraph(footer_text, footer_style))

    doc.build(elements)
    return filename