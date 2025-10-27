from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import Color, HexColor
from reportlab.graphics.shapes import Drawing, Circle, String, Rect
from reportlab.graphics import renderPDF
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
    doc = SimpleDocTemplate(filename, pagesize=letter, 
                           rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=72)
    elements = []
    styles = getSampleStyleSheet()

    # Definir colores corporativos modernos
    azul_principal = HexColor('#1e3a8a')      # Azul corporativo
    verde_secundario = HexColor('#059669')    # Verde institucional
    gris_claro = HexColor('#f8fafc')          # Gris muy claro
    gris_medio = HexColor('#64748b')          # Gris medio
    blanco = HexColor('#ffffff')              # Blanco puro
    negro = HexColor('#1f2937')              # Negro suave

    # Crear estilos personalizados
    def crear_estilos():
        estilos = {}
        
        # Estilo para títulos principales
        estilos['titulo_principal'] = ParagraphStyle(
            'TituloPrincipal',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=azul_principal,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=10
        )
        
        # Estilo para subtítulos
        estilos['subtitulo'] = ParagraphStyle(
            'Subtitulo',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=verde_secundario,
            fontName='Helvetica-Bold',
            spaceAfter=12,
            spaceBefore=8
        )
        
        # Estilo para texto normal
        estilos['texto_normal'] = ParagraphStyle(
            'TextoNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=negro,
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=6
        )
        
        # Estilo para texto en negrita
        estilos['texto_negrita'] = ParagraphStyle(
            'TextoNegrita',
            parent=styles['Normal'],
            fontSize=11,
            textColor=negro,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=6
        )
        
        # Estilo para etiquetas
        estilos['etiqueta'] = ParagraphStyle(
            'Etiqueta',
            parent=styles['Normal'],
            fontSize=10,
            textColor=gris_medio,
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=2
        )
        
        return estilos

    estilos = crear_estilos()

    # Función para crear logo circular
    def crear_logo_circular(texto, color_fondo, color_texto):
        d = Drawing(80, 80)
        d.add(Circle(40, 40, 35, fillColor=color_fondo, strokeColor=color_fondo))
        d.add(String(40, 35, texto, textAnchor='middle', fontSize=14, 
                    fillColor=color_texto, fontName='Helvetica-Bold'))
        return d

    # Header con logos mejorado
    header_elements = []
    
    # Logo de la empresa
    if empresa and empresa.logo_url:
        logo_path = os.path.join('uploads', empresa.logo_url.split('/')[-1])
        if os.path.exists(logo_path):
            try:
                from PIL import Image as PILImage
                with PILImage.open(logo_path) as img:
                    img.verify()
                empresa_logo = Image(logo_path, 1.2*inch, 1.2*inch)
                header_elements.append(empresa_logo)
            except Exception as e:
                print(f"Error cargando logo de empresa: {str(e)}")
                # Crear logo circular como fallback
                logo_circular = crear_logo_circular(empresa_nombre[:3].upper(), azul_principal, blanco)
                header_elements.append(logo_circular)
        else:
            logo_circular = crear_logo_circular(empresa_nombre[:3].upper(), azul_principal, blanco)
            header_elements.append(logo_circular)
    else:
        logo_circular = crear_logo_circular(empresa_nombre[:3].upper(), azul_principal, blanco)
        header_elements.append(logo_circular)
    
    # Logo del cliente
    if visita.cliente.logo_url:
        cliente_logo_path = os.path.join('uploads', visita.cliente.logo_url.split('/')[-1])
        if os.path.exists(cliente_logo_path):
            try:
                from PIL import Image as PILImage
                with PILImage.open(cliente_logo_path) as img:
                    img.verify()
                cliente_logo = Image(cliente_logo_path, 1.2*inch, 1.2*inch)
                header_elements.append(cliente_logo)
            except Exception as e:
                print(f"Error cargando logo de cliente: {str(e)}")
                # Crear logo circular como fallback
                logo_cliente = crear_logo_circular(visita.cliente.nombre[:3].upper(), verde_secundario, blanco)
                header_elements.append(logo_cliente)
        else:
            logo_cliente = crear_logo_circular(visita.cliente.nombre[:3].upper(), verde_secundario, blanco)
            header_elements.append(logo_cliente)
    else:
        logo_cliente = crear_logo_circular(visita.cliente.nombre[:3].upper(), verde_secundario, blanco)
        header_elements.append(logo_cliente)

    # Header principal con logos
    if header_elements:
        logo_table = Table([header_elements], colWidths=[len(header_elements) * 1.5*inch])
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(logo_table)
        elements.append(Spacer(1, 0.3*inch))

    # Título principal del informe
    titulo_principal = Paragraph("INFORME DE PRESTACIÓN DEL SERVICIO", estilos['titulo_principal'])
    elements.append(titulo_principal)
    
    # Información del informe
    info_data = [
        ['ID de Visita:', str(visita.id), 'Fecha:', visita.fecha.strftime('%d/%m/%Y')],
        ['Supervisor:', visita.supervisor.nombre, 'Hora:', visita.fecha.strftime('%H:%M')]
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), azul_principal),
        ('BACKGROUND', (2, 0), (2, 0), azul_principal),
        ('TEXTCOLOR', (0, 0), (0, 0), blanco),
        ('TEXTCOLOR', (2, 0), (2, 0), blanco),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, gris_claro),
        ('BACKGROUND', (1, 0), (1, 0), blanco),
        ('BACKGROUND', (3, 0), (3, 0), blanco),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.4*inch))

    # Información del cliente en tarjeta moderna
    cliente_data = [
        ['INFORMACIÓN DEL CLIENTE', 'INFORMACIÓN DE LA VISITA'],
        ['Cliente:', visita.cliente.nombre, 'Supervisor:', visita.supervisor.nombre],
        ['NIT:', visita.cliente.nit, 'Fecha:', visita.fecha.strftime('%d/%m/%Y')],
        ['Administrador:', visita.cliente.administrador, 'Código:', visita.cliente.tipo_codigo],
        ['Correo:', visita.cliente.correo, 'Hora:', visita.fecha.strftime('%H:%M')]
    ]
    
    cliente_table = Table(cliente_data, colWidths=[2.5*inch, 2.5*inch])
    cliente_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), verde_secundario),
        ('TEXTCOLOR', (0, 0), (1, 0), blanco),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, gris_claro),
        ('BACKGROUND', (0, 1), (-1, -1), blanco),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [blanco, gris_claro]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(cliente_table)
    elements.append(Spacer(1, 0.4*inch))

    # Agrupar zonas por sección
    secciones = {}
    for zona in zonas:
        if zona.seccion not in secciones:
            secciones[zona.seccion] = []
        secciones[zona.seccion].append(zona)

    # Renderizar cada sección con diseño mejorado
    for seccion_nombre, zonas_seccion in secciones.items():
        # Título de sección con icono
        seccion_colors = {
            'Aseo y Limpieza': (verde_secundario, '🧹'),
            'Seguridad y Salud': (HexColor('#dc2626'), '🛡️'),
            'Colaborador': (HexColor('#ea580c'), '👥')
        }
        color, icono = seccion_colors.get(seccion_nombre, (azul_principal, '📋'))
        
        # Crear título de sección con fondo de color
        seccion_header = Table([['']], colWidths=[6*inch])
        seccion_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), color),
            ('HEIGHT', (0, 0), (0, 0), 0.4*inch),
        ]))
        elements.append(seccion_header)
        
        # Título de sección
        seccion_titulo = Paragraph(f"{icono} SECCIÓN: {seccion_nombre.upper()}", estilos['subtitulo'])
        elements.append(seccion_titulo)
        elements.append(Spacer(1, 0.2*inch))
        
        # Crear tarjeta para cada actividad
        for zona in zonas_seccion:
            # Crear tarjeta moderna con sombra
            actividad_data = [
                [zona.concepto_actividad, ""],
                ["Calificación:", zona.calificacion],
                ["Observaciones:", zona.observaciones or 'Sin observaciones']
            ]
            
            actividad_table = Table(actividad_data, colWidths=[4.5*inch, 1.5*inch])
            actividad_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), color),
                ('TEXTCOLOR', (0, 0), (0, 0), blanco),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, 0), 12),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, gris_claro),
                ('BACKGROUND', (0, 1), (-1, -1), blanco),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 1), (0, 1), 20),  # Indentación para etiquetas
            ]))
            elements.append(actividad_table)
            elements.append(Spacer(1, 0.3*inch))
        
        # Agregar fotos de evidencia (solo para Aseo y Seguridad)
        if seccion_nombre in ['Aseo y Limpieza', 'Seguridad y Salud']:
            fotos_data = []
            for zona in zonas_seccion:
                if zona.foto_url:
                    foto_path = os.path.join('uploads', zona.foto_url.split('/')[-1])
                    if os.path.exists(foto_path):
                        try:
                            from PIL import Image as PILImage
                            with PILImage.open(foto_path) as img:
                                img.verify()
                            foto = Image(foto_path, 2.5*inch, 2.5*inch)
                            fotos_data.append(foto)
                        except Exception as e:
                            print(f"Error cargando imagen: {str(e)}")
                            # Crear placeholder para imagen con error
                            error_placeholder = Table([['Imagen no disponible']], colWidths=[2.5*inch])
                            error_placeholder.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (0, 0), gris_claro),
                                ('TEXTCOLOR', (0, 0), (0, 0), gris_medio),
                                ('FONTNAME', (0, 0), (0, 0), 'Helvetica'),
                                ('FONTSIZE', (0, 0), (0, 0), 10),
                                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                                ('HEIGHT', (0, 0), (0, 0), 2.5*inch),
                            ]))
                            fotos_data.append(error_placeholder)
            
            if fotos_data:
                elements.append(Spacer(1, 0.3*inch))
                
                # Título de evidencia
                evidencia_titulo = Paragraph("📸 EVIDENCIA FOTOGRÁFICA", estilos['subtitulo'])
                elements.append(evidencia_titulo)
                elements.append(Spacer(1, 0.2*inch))
                
                # Crear tabla de fotos con diseño mejorado
                fotos_table_data = []
                for i in range(0, len(fotos_data), 2):
                    row = []
                    for j in range(2):
                        if i + j < len(fotos_data):
                            # Crear celda con borde redondeado para cada foto
                            foto_cell = Table([[fotos_data[i + j]]], colWidths=[2.8*inch])
                            foto_cell.setStyle(TableStyle([
                                ('GRID', (0, 0), (0, 0), 2, color),
                                ('BACKGROUND', (0, 0), (0, 0), blanco),
                                ('PADDING', (0, 0), (0, 0), 6),
                                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                            ]))
                            row.append(foto_cell)
                        else:
                            row.append("")
                    fotos_table_data.append(row)
                
                if fotos_table_data:
                    fotos_table = Table(fotos_table_data, colWidths=[2.9*inch, 2.9*inch])
                    fotos_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('PADDING', (0, 0), (-1, -1), 6),
                    ]))
                    elements.append(fotos_table)

    # Sección Conclusiones con diseño mejorado
    if visita.conclusiones:
        elements.append(Spacer(1, 0.5*inch))
        
        # Crear tarjeta de conclusiones moderna
        conclusiones_data = [
            ['CONCLUSIONES', ''],
            [visita.conclusiones, '']
        ]
        
        conclusiones_table = Table(conclusiones_data, colWidths=[5*inch, 1*inch])
        conclusiones_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), azul_principal),
            ('TEXTCOLOR', (0, 0), (0, 0), blanco),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 14),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, gris_claro),
            ('BACKGROUND', (0, 1), (-1, -1), blanco),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(conclusiones_table)
    
    # Footer moderno
    elements.append(Spacer(1, 0.5*inch))
    
    # Línea separadora del footer
    footer_separator = Table([['']], colWidths=[6*inch])
    footer_separator.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), azul_principal),
        ('HEIGHT', (0, 0), (0, 0), 0.1*inch),
    ]))
    elements.append(footer_separator)
    
    # Footer con información de la empresa
    footer_data = [
        [f"{empresa_nombre} | {empresa_direccion} | Tel: {empresa_telefono} | Email: {empresa_correo}"],
        [f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}"]
    ]
    
    footer_table = Table(footer_data, colWidths=[6*inch])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), gris_medio),
        ('TEXTCOLOR', (0, 0), (-1, -1), blanco),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(footer_table)

    doc.build(elements)
    return filename