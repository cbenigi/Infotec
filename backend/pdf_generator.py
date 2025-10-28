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
                           topMargin=36, bottomMargin=72)  # Reducido margen superior de 72 a 36
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

    # Función para crear bloques rectangulares con bordes redondeados
    def crear_bloque_redondeado(color_fondo, color_borde, grosor_borde=1):
        return [
            # Fondo del bloque
            ('BACKGROUND', (0, 0), (-1, -1), color_fondo),
            # Bordes redondeados simulados con líneas
            ('BOX', (0, 0), (-1, -1), grosor_borde, color_borde),
            # Padding interno
            ('PADDING', (0, 0), (-1, -1), 12),
            # Alineación
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]
    
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
    
    # Función para crear tarjetas de actividad con diseño moderno tipo cuadro
    def crear_tarjeta_actividad(titulo, descripcion, calificacion, color_tema, icono="📋"):
        # Crear datos para la tarjeta con diseño de cuadro separado
        tarjeta_data = [
            [f"{icono} {titulo.upper()}"],  # Solo título en la primera fila
            [f"Calificación: {calificacion}"],  # Calificación en segunda fila
            [descripcion]  # Descripción en tercera fila
        ]
        
        # Crear tabla con diseño de tarjeta tipo cuadro
        tarjeta_table = Table(tarjeta_data, colWidths=[6*inch])
        tarjeta_table.setStyle(TableStyle([
            # Título styling - fondo de color
            ('BACKGROUND', (0, 0), (0, 0), color_tema),
            ('TEXTCOLOR', (0, 0), (0, 0), blanco),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 10),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            
            # Calificación styling - fondo gris claro
            ('BACKGROUND', (0, 1), (0, 1), gris_claro),
            ('TEXTCOLOR', (0, 1), (0, 1), color_tema),
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, 1), 9),
            ('ALIGN', (0, 1), (0, 1), 'LEFT'),
            ('VALIGN', (0, 1), (0, 1), 'MIDDLE'),
            
            # Descripción styling - fondo blanco
            ('BACKGROUND', (0, 2), (0, 2), blanco),
            ('FONTNAME', (0, 2), (0, 2), 'Helvetica'),
            ('FONTSIZE', (0, 2), (0, 2), 8),
            ('TEXTCOLOR', (0, 2), (0, 2), negro),
            ('ALIGN', (0, 2), (0, 2), 'LEFT'),
            ('VALIGN', (0, 2), (0, 2), 'TOP'),
            
            # Bordes del cuadro
            ('BOX', (0, 0), (0, 2), 2, color_tema),  # Borde exterior
            ('LINEBELOW', (0, 0), (0, 0), 1, blanco),  # Línea entre título y calificación
            ('LINEBELOW', (0, 1), (0, 1), 1, color_tema),  # Línea entre calificación y descripción
            
            # Padding
            ('PADDING', (0, 0), (0, 2), 10),
        ]))
        
        return tarjeta_table

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
    print(f"DEBUG: === INICIO DEBUG LOGO EMPRESA ===", flush=True)
    print(f"DEBUG: Empresa encontrada: {empresa.nombre if empresa else 'No encontrada'}", flush=True)
    print(f"DEBUG: Logo URL de empresa: {empresa.logo_url if empresa else 'No hay empresa'}", flush=True)
    print(f"DEBUG: Tipo de empresa: {type(empresa)}", flush=True)
    print(f"DEBUG: Empresa es None: {empresa is None}", flush=True)
    
    # Escribir a archivo para debug
    with open('/tmp/debug_logo_empresa.txt', 'w') as f:
        f.write(f"Empresa encontrada: {empresa.nombre if empresa else 'No encontrada'}\n")
        f.write(f"Logo URL de empresa: {empresa.logo_url if empresa else 'No hay empresa'}\n")
    
    if empresa and empresa.logo_url:
        print(f"DEBUG: Intentando cargar logo de empresa: {empresa.logo_url}", flush=True)
        # Intentar diferentes rutas posibles para el logo
        posibles_rutas = [
            empresa.logo_url,  # Ruta completa
            os.path.join('uploads', empresa.logo_url.split('/')[-1]),  # Solo nombre del archivo
            os.path.join('backend/uploads', empresa.logo_url.split('/')[-1]),  # Con backend/
            os.path.join('static/uploads', empresa.logo_url.split('/')[-1]),  # Con static/
        ]
        
        for logo_path in posibles_rutas:
            print(f"DEBUG: Probando ruta: {logo_path}", flush=True)
            if os.path.exists(logo_path):
                print(f"DEBUG: Archivo encontrado en: {logo_path}", flush=True)
                try:
                    from PIL import Image as PILImage
                    with PILImage.open(logo_path) as img:
                        img.verify()
                    empresa_logo = Image(logo_path, 0.6*inch, 0.6*inch)  # Mucho más pequeño
                    header_elements.append(empresa_logo)
                    empresa_logo_cargado = True
                    print(f"✅ Logo de empresa cargado desde: {logo_path}", flush=True)
                    break
                except Exception as e:
                    print(f"❌ Error cargando logo de empresa desde {logo_path}: {str(e)}", flush=True)
                    continue
            else:
                print(f"❌ Archivo no encontrado en: {logo_path}", flush=True)
    
    if not empresa_logo_cargado:
        # Crear logo circular como fallback
        logo_texto = empresa_nombre[:2].upper() if len(empresa_nombre) >= 2 else "E"
        logo_circular = crear_logo_circular(logo_texto, azul_principal, blanco)
        header_elements.append(logo_circular)
        print(f"⚠️ Usando logo circular para empresa: {logo_texto}", flush=True)
    
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

    # Header principal con logos - ultra pegado al techo
    if header_elements:
        logo_table = Table([header_elements], colWidths=[len(header_elements) * 0.8*inch])  # Más pequeño
        logo_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(logo_table)
        elements.append(Spacer(1, 0.005*inch))  # Espaciado aún más mínimo

    # Título principal del informe - ultra pegado al techo
    titulo_principal = Paragraph("INFORME DE PRESTACIÓN DEL SERVICIO", estilos['titulo_principal'])
    elements.append(titulo_principal)
    elements.append(Spacer(1, 0.01*inch))  # Espaciado aún más mínimo
    
    # Información del informe - diseño más compacto
    info_data = [
        ['ID:', str(visita.id), 'Fecha:', visita.fecha.strftime('%d/%m/%Y')],
        ['Supervisor:', visita.supervisor.nombre[:20] + ('...' if len(visita.supervisor.nombre) > 20 else ''), 'Hora:', visita.hora.strftime('%H:%M') if visita.hora else visita.fecha.strftime('%H:%M')]
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
    elements.append(Spacer(1, 0.01*inch))  # Espaciado aún más mínimo

    # Información del cliente en tarjeta moderna con diseño de bloques redondeados
    # Bloque de información del cliente
    cliente_info_data = [
        ['INFORMACIÓN CLIENTE'],
        ['Cliente:', visita.cliente.nombre[:20] + ('...' if len(visita.cliente.nombre) > 20 else '')],
        ['NIT:', visita.cliente.nit[:15] + ('...' if len(visita.cliente.nit) > 15 else '')],
        ['Admin:', visita.cliente.administrador[:18] + ('...' if len(visita.cliente.administrador) > 18 else '')],
        ['Email:', visita.cliente.correo[:30] + ('...' if len(visita.cliente.correo) > 30 else '')]
    ]
    
    cliente_info_table = Table(cliente_info_data, colWidths=[1.2*inch, 2.8*inch])
    cliente_info_table.setStyle(TableStyle([
        # Header styling
        ('SPAN', (0, 0), (1, 0)),  # Combinar columnas para el título
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
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        
        # Bordes redondeados
        *crear_bloque_redondeado(blanco, verde_secundario, 2),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    # Bloque de información de la visita
    visita_info_data = [
        ['INFORMACIÓN VISITA'],
        ['Supervisor:', visita.supervisor.nombre[:18] + ('...' if len(visita.supervisor.nombre) > 18 else '')],
        ['Fecha:', visita.fecha.strftime('%d/%m/%Y')],
        ['Código:', visita.cliente.tipo_codigo[:10] + ('...' if len(visita.cliente.tipo_codigo) > 10 else '')],
        ['Hora:', visita.hora.strftime('%H:%M') if visita.hora else visita.fecha.strftime('%H:%M')]
    ]
    
    visita_info_table = Table(visita_info_data, colWidths=[1.2*inch, 2.8*inch])
    visita_info_table.setStyle(TableStyle([
        # Header styling
        ('SPAN', (0, 0), (1, 0)),  # Combinar columnas para el título
        ('BACKGROUND', (0, 0), (1, 0), azul_principal),
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
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        
        # Bordes redondeados
        *crear_bloque_redondeado(blanco, azul_principal, 2),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    # Crear tabla contenedora para los dos bloques lado a lado
    bloques_info = Table([[cliente_info_table, visita_info_table]], colWidths=[4*inch, 4*inch])
    bloques_info.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(bloques_info)
    elements.append(Spacer(1, 0.02*inch))  # Espaciado entre secciones

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
        elements.append(Spacer(1, 0.01*inch))  # Espaciado aún más reducido
        
        # Crear tarjetas de actividad para cada zona
        for zona in zonas_seccion:
            # Limpiar HTML de los datos
            concepto_limpio = limpiar_html(zona.concepto_actividad)
            calificacion_limpia = limpiar_html(zona.calificacion)
            observaciones_limpias = limpiar_html(zona.observaciones) or 'Sin observaciones'
            
            # Crear tarjeta de actividad con diseño moderno
            tarjeta_actividad = crear_tarjeta_actividad(
                titulo=concepto_limpio,
                descripcion=observaciones_limpias,
                calificacion=calificacion_limpia,
                color_tema=color,
                icono=icono
            )
            
            # Crear contenedor para la tarjeta y evidencia fotográfica
            if zona.foto_url:
                # Intentar diferentes rutas para la foto
                posibles_rutas_foto = [
                    zona.foto_url,  # Ruta completa
                    os.path.join('uploads', zona.foto_url.split('/')[-1]),  # Solo nombre del archivo
                    os.path.join('backend/uploads', zona.foto_url.split('/')[-1]),  # Con backend/
                    os.path.join('static/uploads', zona.foto_url.split('/')[-1]),  # Con static/
                ]
                
                foto_cargada = False
                for foto_path in posibles_rutas_foto:
                    if os.path.exists(foto_path):
                        try:
                            from PIL import Image as PILImage
                            with PILImage.open(foto_path) as img:
                                img.verify()
                            # Foto más grande: 2x1.5 inch para mejor visibilidad
                            foto = Image(foto_path, 2*inch, 1.5*inch)
                            
                            # Crear tabla con tarjeta arriba y foto abajo
                            actividad_con_evidencia = Table([
                                [tarjeta_actividad],
                                [foto]
                            ], colWidths=[6*inch])
                            actividad_con_evidencia.setStyle(TableStyle([
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('PADDING', (0, 0), (-1, -1), 5),
                                # Borde alrededor de toda la evidencia
                                ('BOX', (0, 0), (0, 1), 1, gris_medio),
                            ]))
                            elements.append(actividad_con_evidencia)
                            foto_cargada = True
                            print(f"✅ Evidencia cargada desde: {foto_path}")
                            break
                        except Exception as e:
                            print(f"❌ Error cargando imagen desde {foto_path}: {str(e)}")
                            continue
                
                if not foto_cargada:
                    print(f"⚠️ No se pudo cargar evidencia para: {zona.concepto_actividad}")
                    elements.append(tarjeta_actividad)
            else:
                elements.append(tarjeta_actividad)
            
            elements.append(Spacer(1, 0.03*inch))  # Espaciado entre tarjetas
        
        elements.append(Spacer(1, 0.02*inch))  # Espaciado entre secciones aún más reducido

    # Sección Conclusiones con diseño de bloque redondeado
    if visita.conclusiones:
        elements.append(Spacer(1, 0.05*inch))  # Espaciado aún más reducido
        
        # Limpiar HTML de las conclusiones
        conclusiones_limpias = limpiar_html(visita.conclusiones)
        
        # Crear bloque de conclusiones con diseño moderno y texto que se ajusta
        # Crear un estilo para el texto de conclusiones que se ajuste automáticamente
        estilo_conclusiones = ParagraphStyle(
            'ConclusionesTexto',
            parent=estilos['texto_normal'],
            fontSize=9,
            textColor=negro,
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=6,
            spaceBefore=6,
            leftIndent=0,
            rightIndent=0,
            wordWrap='CJK'  # Permite que el texto se ajuste automáticamente
        )
        
        # Crear el texto de conclusiones como Paragraph para que se ajuste
        conclusiones_paragraph = Paragraph(conclusiones_limpias, estilo_conclusiones)
        
        conclusiones_data = [
            ['CONCLUSIONES'],
            [conclusiones_paragraph]
        ]
        
        conclusiones_table = Table(conclusiones_data, colWidths=[6*inch])
        conclusiones_table.setStyle(TableStyle([
            # Header styling
            ('SPAN', (0, 0), (0, 0)),  # Combinar columnas para el título
            ('BACKGROUND', (0, 0), (0, 0), azul_principal),
            ('TEXTCOLOR', (0, 0), (0, 0), blanco),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 12),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            
            # Content styling
            ('BACKGROUND', (0, 1), (0, 1), blanco),
            ('ALIGN', (0, 1), (0, 1), 'LEFT'),
            ('VALIGN', (0, 1), (0, 1), 'TOP'),
            
            # Bordes redondeados
            *crear_bloque_redondeado(blanco, azul_principal, 2),
            ('PADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(conclusiones_table)
    
    # Footer moderno
    elements.append(Spacer(1, 0.05*inch))  # Espaciado aún más reducido
    
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