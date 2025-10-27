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
    import sys
    print(f"=== INICIANDO GENERACIÓN DE PDF PARA VISITA {visita_id} ===", flush=True)
    sys.stdout.flush()
    
    # Escribir a archivo para debug
    with open('/tmp/debug_pdf.txt', 'a') as f:
        f.write(f"=== INICIANDO GENERACIÓN DE PDF PARA VISITA {visita_id} ===\n")
        f.flush()
    
    visita = Visita.query.get(visita_id)
    if not visita:
        print(f"ERROR: No se encontró visita con ID {visita_id}", flush=True)
        sys.stdout.flush()
        with open('/tmp/debug_pdf.txt', 'a') as f:
            f.write(f"ERROR: No se encontró visita con ID {visita_id}\n")
            f.flush()
        return None

    # Obtener zonas de la visita
    print("DEBUG: Obteniendo zonas de la visita...", flush=True)
    sys.stdout.flush()
    zonas = Zona.query.filter_by(visita_id=visita_id).all()
    print(f"DEBUG: Se encontraron {len(zonas)} zonas para la visita {visita_id}", flush=True)
    sys.stdout.flush()
    
    with open('/tmp/debug_pdf.txt', 'a') as f:
        f.write(f"DEBUG: Se encontraron {len(zonas)} zonas para la visita {visita_id}\n")
        f.flush()
    
    if not zonas:
        print("ERROR: No se encontraron zonas para la visita", flush=True)
        sys.stdout.flush()
        with open('/tmp/debug_pdf.txt', 'a') as f:
            f.write("ERROR: No se encontraron zonas para la visita\n")
            f.flush()
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

    # Función para crear bordes redondos elegantes
    def crear_bordes_redondos(color_principal, color_secundario):
        return [
            # Bordes principales más gruesos para efecto redondeado
            ('GRID', (0, 0), (-1, -1), 2.5, color_principal),
            # Bordes internos más suaves
            ('LINEBELOW', (0, 0), (-1, 0), 3, color_principal),
            ('LINEABOVE', (0, 0), (-1, 0), 3, color_principal),
            ('LINEBEFORE', (1, 0), (1, -1), 2, color_secundario),
            ('LINEAFTER', (0, 0), (0, -1), 2, color_secundario),
            ('LINEBEFORE', (0, 0), (0, -1), 2, color_secundario),
        ]

    # Función para limpiar HTML de los textos
    def limpiar_html(texto):
        if not texto:
            return texto
        import re
        # Convertir a string si no lo es
        texto = str(texto)
        
        # TEST: Imprimir el texto original
        print(f"ANTES de limpiar: '{texto}'")
        
        # Remover etiquetas HTML específicas más comunes
        texto = re.sub(r'<b[^>]*>', '', texto)  # <b> y <b atributos>
        texto = re.sub(r'</b>', '', texto)      # </b>
        texto = re.sub(r'<i[^>]*>', '', texto)  # <i> y <i atributos>
        texto = re.sub(r'</i>', '', texto)      # </i>
        texto = re.sub(r'<u[^>]*>', '', texto)  # <u> y <u atributos>
        texto = re.sub(r'</u>', '', texto)      # </u>
        texto = re.sub(r'<strong[^>]*>', '', texto)  # <strong>
        texto = re.sub(r'</strong>', '', texto)      # </strong>
        texto = re.sub(r'<em[^>]*>', '', texto)      # <em>
        texto = re.sub(r'</em>', '', texto)          # </em>
        # Remover cualquier etiqueta HTML restante
        texto = re.sub(r'<[^>]+>', '', texto)
        # Limpiar espacios extra y caracteres especiales
        texto = ' '.join(texto.split())
        # Limpiar caracteres de escape
        texto = texto.replace('&nbsp;', ' ')
        texto = texto.replace('&amp;', '&')
        texto = texto.replace('&lt;', '<')
        texto = texto.replace('&gt;', '>')
        
        # TEST: Imprimir el texto después de limpiar
        print(f"DESPUÉS de limpiar: '{texto}'")
        
        return texto

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
                # Crear logo circular como fallback con texto más descriptivo
                logo_texto = empresa_nombre[:2].upper() if len(empresa_nombre) >= 2 else "E"
                logo_circular = crear_logo_circular(logo_texto, azul_principal, blanco)
                header_elements.append(logo_circular)
        else:
            logo_texto = empresa_nombre[:2].upper() if len(empresa_nombre) >= 2 else "E"
            logo_circular = crear_logo_circular(logo_texto, azul_principal, blanco)
            header_elements.append(logo_circular)
    else:
        logo_texto = empresa_nombre[:2].upper() if len(empresa_nombre) >= 2 else "E"
        logo_circular = crear_logo_circular(logo_texto, azul_principal, blanco)
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
    
    # Información del informe - diseño más compacto
    info_data = [
        ['ID:', str(visita.id), 'Fecha:', visita.fecha.strftime('%d/%m/%Y')],
        ['Supervisor:', visita.supervisor.nombre[:20] + ('...' if len(visita.supervisor.nombre) > 20 else ''), 'Hora:', visita.fecha.strftime('%H:%M')]
    ]
    
    info_table = Table(info_data, colWidths=[0.8*inch, 1.8*inch, 0.8*inch, 1.8*inch])
    info_table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (0, 0), azul_principal),
        ('BACKGROUND', (2, 0), (2, 0), azul_principal),
        ('TEXTCOLOR', (0, 0), (0, 0), blanco),
        ('TEXTCOLOR', (2, 0), (2, 0), blanco),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        
        # Content styling
        ('BACKGROUND', (1, 0), (1, 0), blanco),
        ('BACKGROUND', (3, 0), (3, 0), blanco),
        
        # Alignment
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Beautiful borders with matching colors
        *crear_bordes_redondos(azul_principal, gris_medio),
        
        # Padding
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.4*inch))

    # Información del cliente en tarjeta moderna - diseño simple y elegante
    cliente_data = [
        ['INFORMACIÓN CLIENTE', 'INFORMACIÓN VISITA'],
        ['Cliente:', visita.cliente.nombre[:15] + ('...' if len(visita.cliente.nombre) > 15 else ''), 'Supervisor:', visita.supervisor.nombre[:12] + ('...' if len(visita.supervisor.nombre) > 12 else '')],
        ['NIT:', visita.cliente.nit[:10] + ('...' if len(visita.cliente.nit) > 10 else ''), 'Fecha:', visita.fecha.strftime('%d/%m/%Y')],
        ['Admin:', visita.cliente.administrador[:12] + ('...' if len(visita.cliente.administrador) > 12 else ''), 'Código:', visita.cliente.tipo_codigo[:6] + ('...' if len(visita.cliente.tipo_codigo) > 6 else '')],
        ['Email:', visita.cliente.correo[:15] + ('...' if len(visita.cliente.correo) > 15 else ''), 'Hora:', visita.fecha.strftime('%H:%M')]
    ]
    
    cliente_table = Table(cliente_data, colWidths=[2.0*inch, 2.0*inch])
    cliente_table.setStyle(TableStyle([
        # Header styling - simple y elegante
        ('BACKGROUND', (0, 0), (1, 0), verde_secundario),
        ('TEXTCOLOR', (0, 0), (1, 0), blanco),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 10),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
        
        # Content styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), blanco),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [blanco, gris_claro]),
        
        # Alignment
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        
        # Beautiful borders
        ('GRID', (0, 0), (-1, -1), 2, verde_secundario),
        ('LINEBELOW', (0, 0), (1, 0), 3, verde_secundario),
        ('LINEABOVE', (0, 0), (1, 0), 3, verde_secundario),
        ('LINEBEFORE', (1, 0), (1, -1), 2, verde_secundario),
        
        # Padding
        ('PADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 1), (-1, -1), 4),
        ('RIGHTPADDING', (0, 1), (-1, -1), 4),
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
            # Debug: imprimir datos originales
            print(f"DEBUG - Concepto original: '{zona.concepto_actividad}'")
            print(f"DEBUG - Calificación original: '{zona.calificacion}'")
            print(f"DEBUG - Observaciones originales: '{zona.observaciones}'")
            
            # Limpiar HTML de los datos
            concepto_limpio = limpiar_html(zona.concepto_actividad)
            calificacion_limpia = limpiar_html(zona.calificacion)
            observaciones_limpias = limpiar_html(zona.observaciones) or 'Sin observaciones'
            
            # Debug: imprimir datos limpios
            print(f"DEBUG - Concepto limpio: '{concepto_limpio}'")
            print(f"DEBUG - Calificación limpia: '{calificacion_limpia}'")
            print(f"DEBUG - Observaciones limpias: '{observaciones_limpias}'")
            print("---")
            
            # Crear tarjeta moderna con sombra usando Paragraph para evitar HTML
            actividad_data = [
                [Paragraph(concepto_limpio, estilos['texto_negrita']), ""],
                [Paragraph("Calificación:", estilos['texto_negrita']), Paragraph(calificacion_limpia, estilos['texto_normal'])],
                [Paragraph("Observaciones:", estilos['texto_negrita']), Paragraph(observaciones_limpias, estilos['texto_normal'])]
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
        
        # Limpiar HTML de las conclusiones
        conclusiones_limpias = limpiar_html(visita.conclusiones)
        
        # Crear tarjeta de conclusiones moderna
        conclusiones_data = [
            [Paragraph('CONCLUSIONES', estilos['texto_negrita']), ''],
            [Paragraph(conclusiones_limpias, estilos['texto_normal']), '']
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