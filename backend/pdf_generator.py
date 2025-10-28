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

    # Obtener datos de la empresa del supervisor
    supervisor = User.query.get(visita.supervisor_id)
    empresa = None
    if supervisor:
        empresa = Empresa.query.filter_by(user_id=supervisor.id).first()
        print(f"DEBUG: Supervisor encontrado: {supervisor.email}")
        print(f"DEBUG: Empresa encontrada: {empresa.nombre if empresa else 'No encontrada'}")
        if empresa:
            print(f"DEBUG: Logo URL de empresa: {empresa.logo_url}")
    else:
        print("DEBUG: No se encontró supervisor")
    
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

    # Crear estilos personalizados con fuentes elegantes similares a Archivo
    # Nota: ReportLab no puede usar Google Fonts directamente, pero Helvetica es muy similar a Archivo
    def crear_estilos():
        estilos = {}
        
        # Estilo para títulos principales - más compacto con fuente elegante
        estilos['titulo_principal'] = ParagraphStyle(
            'TituloPrincipal',
            parent=styles['Heading1'],
            fontSize=18,  # Reducido de 24 a 18
            textColor=azul_principal,
            fontName='Helvetica-Bold',  # Similar a Archivo Bold
            alignment=TA_CENTER,
            spaceAfter=12,  # Reducido de 20 a 12
            spaceBefore=6   # Reducido de 10 a 6
        )
        
        # Estilo para subtítulos - más compacto con fuente elegante
        estilos['subtitulo'] = ParagraphStyle(
            'Subtitulo',
            parent=styles['Heading2'],
            fontSize=11,  # Reducido de 16 a 11
            textColor=verde_secundario,
            fontName='Helvetica-Bold',  # Similar a Archivo Bold
            spaceAfter=6,   # Reducido de 12 a 6
            spaceBefore=4   # Reducido de 8 a 4
        )
        
        # Estilo para texto normal - más compacto con fuente elegante
        estilos['texto_normal'] = ParagraphStyle(
            'TextoNormal',
            parent=styles['Normal'],
            fontSize=8,  # Reducido de 11 a 8
            textColor=negro,
            fontName='Helvetica',  # Similar a Archivo Regular
            alignment=TA_LEFT,
            spaceAfter=3  # Reducido de 6 a 3
        )
        
        # Estilo para texto en negrita - más compacto con fuente elegante
        estilos['texto_negrita'] = ParagraphStyle(
            'TextoNegrita',
            parent=styles['Normal'],
            fontSize=8,  # Reducido de 11 a 8
            textColor=negro,
            fontName='Helvetica-Bold',  # Similar a Archivo Bold
            alignment=TA_LEFT,
            spaceAfter=3  # Reducido de 6 a 3
        )
        
        # Estilo para etiquetas - más compacto
        estilos['etiqueta'] = ParagraphStyle(
            'Etiqueta',
            parent=styles['Normal'],
            fontSize=7,  # Reducido de 10 a 7
            textColor=gris_medio,
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=1  # Reducido de 2 a 1
        )
        
        # Nuevos estilos para layout compacto con fuentes elegantes
        estilos['concepto'] = ParagraphStyle(
            'Concepto',
            parent=styles['Normal'],
            fontSize=7,
            textColor=negro,
            fontName='Helvetica-Bold',  # Similar a Archivo Bold
            alignment=TA_LEFT,
            spaceAfter=1
        )
        
        estilos['descripcion'] = ParagraphStyle(
            'Descripcion',
            parent=styles['Normal'],
            fontSize=7,
            textColor=negro,
            fontName='Helvetica',  # Similar a Archivo Regular
            alignment=TA_LEFT,
            spaceAfter=1
        )
        
        estilos['calificacion'] = ParagraphStyle(
            'Calificacion',
            parent=styles['Normal'],
            fontSize=6,
            textColor=verde_secundario,
            fontName='Helvetica-Bold',  # Similar a Archivo Bold
            alignment=TA_CENTER,
            spaceAfter=1
        )
        
        return estilos

    estilos = crear_estilos()

    # Función para crear logo circular - más pequeño
    def crear_logo_circular(texto, color_fondo, color_texto):
        d = Drawing(60, 60)  # Reducido de 80x80 a 60x60
        d.add(Circle(30, 30, 25, fillColor=color_fondo, strokeColor=color_fondo))  # Reducido de 35 a 25
        d.add(String(30, 26, texto, textAnchor='middle', fontSize=10,  # Reducido de 14 a 10
                    fillColor=color_texto, fontName='Helvetica-Bold'))
        return d

    # Función para crear bordes minimalistas y modernos
    def crear_bordes_modernos(color_principal, color_secundario):
        return [
            # Bordes sutiles y delgados
            ('GRID', (0, 0), (-1, -1), 0.5, color_principal),  # Muy delgado
            # Bordes superiores e inferiores más prominentes
            ('LINEBELOW', (0, 0), (-1, 0), 1, color_principal),
            ('LINEABOVE', (0, 0), (-1, 0), 1, color_principal),
            # Bordes laterales sutiles
            ('LINEBEFORE', (1, 0), (1, -1), 0.5, color_secundario),
            ('LINEAFTER', (0, 0), (0, -1), 0.5, color_secundario),
        ]
    
    # Función para bordes ultra minimalistas
    def crear_bordes_minimalistas(color_principal):
        return [
            # Solo bordes superiores e inferiores
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, color_principal),
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, color_principal),
            # Bordes laterales muy sutiles
            ('LINEBEFORE', (1, 0), (1, -1), 0.3, color_principal),
            ('LINEAFTER', (0, 0), (0, -1), 0.3, color_principal),
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
    
    # Logo de la empresa - debug mejorado
    empresa_logo_cargado = False
    print(f"DEBUG: Empresa encontrada: {empresa.nombre if empresa else 'No encontrada'}")
    print(f"DEBUG: Logo URL de empresa: {empresa.logo_url if empresa else 'No hay empresa'}")
    
    if empresa and empresa.logo_url:
        print(f"DEBUG: Intentando cargar logo de empresa: {empresa.logo_url}")
        # Intentar diferentes rutas posibles para el logo
        posibles_rutas = [
            empresa.logo_url,  # Ruta completa
            os.path.join('uploads', empresa.logo_url.split('/')[-1]),  # Solo nombre del archivo
            os.path.join('backend/uploads', empresa.logo_url.split('/')[-1]),  # Con backend/
            os.path.join('static/uploads', empresa.logo_url.split('/')[-1]),  # Con static/
        ]
        
        for logo_path in posibles_rutas:
            print(f"DEBUG: Probando ruta: {logo_path}")
            if os.path.exists(logo_path):
                print(f"DEBUG: Archivo encontrado en: {logo_path}")
                try:
                    from PIL import Image as PILImage
                    with PILImage.open(logo_path) as img:
                        img.verify()
                    empresa_logo = Image(logo_path, 0.6*inch, 0.6*inch)  # Mucho más pequeño
                    header_elements.append(empresa_logo)
                    empresa_logo_cargado = True
                    print(f"✅ Logo de empresa cargado desde: {logo_path}")
                    break
                except Exception as e:
                    print(f"❌ Error cargando logo de empresa desde {logo_path}: {str(e)}")
                    continue
            else:
                print(f"❌ Archivo no encontrado en: {logo_path}")
    
    if not empresa_logo_cargado:
        # Crear logo circular como fallback
        logo_texto = empresa_nombre[:2].upper() if len(empresa_nombre) >= 2 else "E"
        logo_circular = crear_logo_circular(logo_texto, azul_principal, blanco)
        header_elements.append(logo_circular)
        print(f"⚠️ Usando logo circular para empresa: {logo_texto}")
    
    # Logo del cliente - mejorado
    cliente_logo_cargado = False
    if visita.cliente.logo_url:
        # Intentar diferentes rutas posibles para el logo del cliente
        posibles_rutas_cliente = [
            visita.cliente.logo_url,  # Ruta completa
            os.path.join('uploads', visita.cliente.logo_url.split('/')[-1]),  # Solo nombre del archivo
            os.path.join('backend/uploads', visita.cliente.logo_url.split('/')[-1]),  # Con backend/
            os.path.join('static/uploads', visita.cliente.logo_url.split('/')[-1]),  # Con static/
        ]
        
        for logo_path in posibles_rutas_cliente:
            if os.path.exists(logo_path):
                try:
                    from PIL import Image as PILImage
                    with PILImage.open(logo_path) as img:
                        img.verify()
                    cliente_logo = Image(logo_path, 0.6*inch, 0.6*inch)  # Mucho más pequeño
                    header_elements.append(cliente_logo)
                    cliente_logo_cargado = True
                    print(f"Logo de cliente cargado desde: {logo_path}")
                    break
                except Exception as e:
                    print(f"Error cargando logo de cliente desde {logo_path}: {str(e)}")
                    continue
    
    if not cliente_logo_cargado:
        # Crear logo circular como fallback
        logo_texto = visita.cliente.nombre[:2].upper() if len(visita.cliente.nombre) >= 2 else "C"
        logo_circular = crear_logo_circular(logo_texto, verde_secundario, blanco)
        header_elements.append(logo_circular)
        print(f"Usando logo circular para cliente: {logo_texto}")

    # Header principal con logos - más compacto
    if header_elements:
        logo_table = Table([header_elements], colWidths=[len(header_elements) * 0.8*inch])  # Más pequeño
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(logo_table)
        elements.append(Spacer(1, 0.1*inch))  # Espaciado reducido

    # Título principal del informe - más compacto
    titulo_principal = Paragraph("INFORME DE PRESTACIÓN DEL SERVICIO", estilos['titulo_principal'])
    elements.append(titulo_principal)
    elements.append(Spacer(1, 0.2*inch))  # Espaciado reducido
    
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
        ('FONTSIZE', (0, 0), (-1, -1), 7),  # Más pequeño
        
        # Content styling
        ('BACKGROUND', (1, 0), (1, 0), blanco),
        ('BACKGROUND', (3, 0), (3, 0), blanco),
        
        # Alignment
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Bordes minimalistas modernos
        *crear_bordes_minimalistas(azul_principal),
        
        # Padding reducido
        ('PADDING', (0, 0), (-1, -1), 3),  # Reducido de 6 a 3
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.2*inch))  # Espaciado reducido

    # Información del cliente en tarjeta moderna - diseño con 4 columnas
    cliente_data = [
        ['INFORMACIÓN CLIENTE', '', 'INFORMACIÓN VISITA', ''],
        ['Cliente:', visita.cliente.nombre[:20] + ('...' if len(visita.cliente.nombre) > 20 else ''), 'Supervisor:', visita.supervisor.nombre[:18] + ('...' if len(visita.supervisor.nombre) > 18 else '')],
        ['NIT:', visita.cliente.nit[:15] + ('...' if len(visita.cliente.nit) > 15 else ''), 'Fecha:', visita.fecha.strftime('%d/%m/%Y')],
        ['Admin:', visita.cliente.administrador[:18] + ('...' if len(visita.cliente.administrador) > 18 else ''), 'Código:', visita.cliente.tipo_codigo[:10] + ('...' if len(visita.cliente.tipo_codigo) > 10 else '')],
        ['Email:', visita.cliente.correo[:30] + ('...' if len(visita.cliente.correo) > 30 else ''), 'Hora:', visita.fecha.strftime('%H:%M')]
    ]
    
    cliente_table = Table(cliente_data, colWidths=[0.8*inch, 1.2*inch, 0.8*inch, 1.2*inch])  # Columnas más anchas para valores
    cliente_table.setStyle(TableStyle([
        # Header styling - combinar columnas 1-2 y 3-4
        ('SPAN', (0, 0), (1, 0)),  # Combinar columnas 0-1 para "INFORMACIÓN CLIENTE"
        ('SPAN', (2, 0), (3, 0)),  # Combinar columnas 2-3 para "INFORMACIÓN VISITA"
        ('BACKGROUND', (0, 0), (1, 0), verde_secundario),
        ('BACKGROUND', (2, 0), (3, 0), verde_secundario),
        ('TEXTCOLOR', (0, 0), (3, 0), blanco),
        ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (3, 0), 10),
        ('ALIGN', (0, 0), (3, 0), 'CENTER'),
        ('VALIGN', (0, 0), (3, 0), 'MIDDLE'),
        
        # Content styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, -1), blanco),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [blanco, gris_claro]),
        
        # Alignment
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        
        # Bordes minimalistas modernos
        *crear_bordes_minimalistas(verde_secundario),
        
        # Padding reducido
        ('PADDING', (0, 0), (-1, -1), 3),  # Reducido de 6 a 3
        ('LEFTPADDING', (0, 1), (-1, -1), 2),  # Reducido de 4 a 2
        ('RIGHTPADDING', (0, 1), (-1, -1), 2),  # Reducido de 4 a 2
    ]))
    elements.append(cliente_table)
    elements.append(Spacer(1, 0.2*inch))  # Espaciado reducido

    # Agrupar zonas por sección
    secciones = {}
    for zona in zonas:
        if zona.seccion not in secciones:
            secciones[zona.seccion] = []
        secciones[zona.seccion].append(zona)

    # Renderizar cada sección con diseño compacto
    for seccion_nombre, zonas_seccion in secciones.items():
        # Título de sección compacto
        seccion_colors = {
            'Aseo y Limpieza': (verde_secundario, '🧹'),
            'Seguridad y Salud': (HexColor('#dc2626'), '🛡️'),
            'Colaborador': (HexColor('#ea580c'), '👥')
        }
        color, icono = seccion_colors.get(seccion_nombre, (azul_principal, '📋'))
        
        # Título de sección ultra compacto
        seccion_titulo = Paragraph(f"{icono} {seccion_nombre.upper()}", estilos['subtitulo'])
        elements.append(seccion_titulo)
        elements.append(Spacer(1, 0.02*inch))  # Espaciado ultra reducido
        
        # Crear layout compacto para cada zona
        for zona in zonas_seccion:
            # Limpiar HTML de los datos
            concepto_limpio = limpiar_html(zona.concepto_actividad)
            calificacion_limpia = limpiar_html(zona.calificacion)
            observaciones_limpias = limpiar_html(zona.observaciones) or 'Sin observaciones'
            
            # Layout compacto: concepto arriba, descripción abajo, evidencia al lado
            zona_data = []
            
            # Fila 1: Concepto (izquierda) + Calificación (derecha)
            concepto_texto = Paragraph(concepto_limpio, estilos['concepto'])
            calificacion_texto = Paragraph(f"Calificación: {calificacion_limpia}", estilos['calificacion'])
            zona_data.append([concepto_texto, calificacion_texto])
            
            # Fila 2: Descripción (izquierda) + Evidencia (derecha)
            descripcion_texto = Paragraph(observaciones_limpias, estilos['descripcion'])
            
            # Evidencia (foto si existe)
            if zona.foto_url and seccion_nombre in ['Aseo y Limpieza', 'Seguridad y Salud']:
                foto_path = os.path.join('uploads', zona.foto_url.split('/')[-1])
                if os.path.exists(foto_path):
                    try:
                        from PIL import Image as PILImage
                        with PILImage.open(foto_path) as img:
                            img.verify()
                        # Foto más pequeña: 0.8x0.8 inch
                        foto = Image(foto_path, 0.8*inch, 0.8*inch)
                        zona_data.append([descripcion_texto, foto])
                    except Exception as e:
                        print(f"Error cargando imagen: {str(e)}")
                        error_texto = Paragraph("Imagen no disponible", estilos['descripcion'])
                        zona_data.append([descripcion_texto, error_texto])
                else:
                    zona_data.append([descripcion_texto, ""])
            else:
                zona_data.append([descripcion_texto, ""])
            
            # Crear tabla compacta
            zona_table = Table(zona_data, colWidths=[3.5*inch, 2.0*inch])
            zona_table.setStyle(TableStyle([
                # Bordes sutiles
                ('GRID', (0, 0), (-1, -1), 0.5, gris_claro),
                ('BACKGROUND', (0, 0), (0, 0), color),  # Header con color de sección
                ('TEXTCOLOR', (0, 0), (0, 0), blanco),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, 0), 7),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 4),  # Padding reducido
                ('BACKGROUND', (0, 1), (-1, -1), blanco),
            ]))
            elements.append(zona_table)
            elements.append(Spacer(1, 0.05*inch))  # Espaciado ultra mínimo entre zonas
        
        elements.append(Spacer(1, 0.05*inch))  # Espaciado entre secciones ultra reducido

    # Sección Conclusiones con diseño mejorado
    if visita.conclusiones:
        elements.append(Spacer(1, 0.1*inch))  # Espaciado ultra reducido
        
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
    elements.append(Spacer(1, 0.1*inch))  # Espaciado ultra reducido
    
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