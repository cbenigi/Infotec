import os
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from jinja2 import Environment, FileSystemLoader
from models import Visita, Zona, User, Empresa
import re
from datetime import datetime

class HTMLPDFGenerator:
    def __init__(self, upload_folder=None):
        # Configurar Jinja2
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # Configurar upload folder
        self.upload_folder = upload_folder or os.environ.get('UPLOAD_FOLDER', '/app/uploads')
        
        # Configurar WeasyPrint
        self.font_config = FontConfiguration()
        self.css = CSS(string='''
            @page {
                size: A4;
                margin: 12mm 15mm;
            }
            body {
                font-family: Arial, sans-serif;
                font-size: 12px;
                line-height: 1.4;
                color: #333;
            }
        ''', font_config=self.font_config)
    
    def limpiar_html(self, texto):
        """Limpiar HTML de los textos"""
        if not texto:
            return texto
        # Remover tags HTML pero mantener el contenido
        texto_limpio = re.sub(r'<[^>]+>', '', str(texto))
        return texto_limpio.strip()
    
    def obtener_actividades_por_seccion(self, zonas, seccion_nombre):
        """Obtener actividades filtradas por sección"""
        actividades = []
        for zona in zonas:
            if zona.seccion and zona.seccion.lower() == seccion_nombre.lower():
                actividades.append({
                    'concepto_actividad': self.limpiar_html(zona.concepto_actividad),
                    'calificacion': self.limpiar_html(zona.calificacion),
                    'observaciones': self.limpiar_html(zona.observaciones) or 'Sin observaciones',
                    'foto_url': self.convertir_foto_a_html(self.obtener_ruta_foto(zona.foto_url)) if zona.foto_url else None
                })
        return actividades
    
    def obtener_ruta_foto(self, foto_url):
        """Obtener la ruta correcta de la foto"""
        if not foto_url:
            return None
        
        print(f"=== DEBUG OBTENER RUTA FOTO ===")
        print(f"DEBUG: Foto URL desde BD: '{foto_url}'")
        
        # Base directory del archivo actual
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"DEBUG: Base dir del generador: {base_dir}")
        print(f"DEBUG: Upload folder configurado: {self.upload_folder}")
        
        nombre = foto_url.split('/')[-1]
        print(f"DEBUG: Nombre del archivo extraído: '{nombre}'")
        
        posibles_rutas = [
            os.path.join(self.upload_folder, nombre),  # Usar upload_folder configurado
            os.path.join(base_dir, 'uploads', nombre),  # backend/uploads/nombre
            os.path.join(base_dir, '..', 'uploads', nombre),  # uploads/nombre desde backend
            os.path.join('uploads', nombre),
            os.path.join('backend', 'uploads', nombre),
            os.path.join('static', 'uploads', nombre),
            nombre,
        ]
        
        print(f"DEBUG: Rutas que se van a probar:")
        for i, ruta in enumerate(posibles_rutas, 1):
            abs_ruta = os.path.abspath(ruta)
            existe = os.path.exists(ruta)
            print(f"  {i}. {ruta}")
            print(f"     Absoluta: {abs_ruta}")
            print(f"     Existe: {existe}")
            if existe:
                print(f"DEBUG: ✅ FOTO ENCONTRADA EN: {ruta}")
                return ruta
        
        print(f"DEBUG: ❌ NO SE ENCONTRÓ LA FOTO: {foto_url}")
        return None
    
    def obtener_logo_empresa(self, empresa):
        """Obtener la ruta del logo de la empresa"""
        print(f"=== DEBUG OBTENER LOGO EMPRESA ===")
        if not empresa:
            print("DEBUG: No se pasó objeto empresa")
            return None
        if not empresa.logo_url:
            print("DEBUG: Empresa sin logo_url")
            return None
        
        print(f"DEBUG: Empresa: {empresa.nombre}")
        print(f"DEBUG: Logo URL desde BD: '{empresa.logo_url}'")
        
        # Base directory del archivo actual
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"DEBUG: Base dir del generador: {base_dir}")
        print(f"DEBUG: Upload folder configurado: {self.upload_folder}")
        
        nombre = empresa.logo_url.split('/')[-1]
        print(f"DEBUG: Nombre del archivo extraído: '{nombre}'")
        
        posibles_rutas = [
            os.path.join(self.upload_folder, nombre),  # Usar upload_folder configurado
            os.path.join(base_dir, 'uploads', nombre),  # backend/uploads/nombre
            os.path.join(base_dir, '..', 'uploads', nombre),  # uploads/nombre desde backend
            os.path.join('uploads', nombre),
            os.path.join('backend', 'uploads', nombre),
            os.path.join('static', 'uploads', nombre),
        ]
        
        print(f"DEBUG: Rutas que se van a probar:")
        for i, ruta in enumerate(posibles_rutas, 1):
            abs_ruta = os.path.abspath(ruta)
            existe = os.path.exists(ruta)
            print(f"  {i}. {ruta}")
            print(f"     Absoluta: {abs_ruta}")
            print(f"     Existe: {existe}")
            if existe:
                print(f"DEBUG: ✅ LOGO EMPRESA ENCONTRADO EN: {ruta}")
                return ruta
        
        print(f"DEBUG: ❌ NO SE ENCONTRÓ EL LOGO EMPRESA: {empresa.logo_url}")
        return None
    
    def obtener_logo_cliente(self, cliente):
        """Obtener la ruta del logo del cliente"""
        print(f"=== DEBUG OBTENER LOGO CLIENTE ===")
        if not cliente:
            print("DEBUG: No se pasó objeto cliente")
            return None
        if not cliente.logo_url:
            print("DEBUG: Cliente sin logo_url")
            return None
        
        print(f"DEBUG: Cliente: {cliente.nombre}")
        print(f"DEBUG: Logo URL desde BD: '{cliente.logo_url}'")
        
        # Base directory del archivo actual
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"DEBUG: Base dir del generador: {base_dir}")
        print(f"DEBUG: Upload folder configurado: {self.upload_folder}")
        
        nombre = cliente.logo_url.split('/')[-1]
        print(f"DEBUG: Nombre del archivo extraído: '{nombre}'")
        
        posibles_rutas = [
            os.path.join(self.upload_folder, nombre),  # Usar upload_folder configurado
            os.path.join(base_dir, 'uploads', nombre),  # backend/uploads/nombre
            os.path.join(base_dir, '..', 'uploads', nombre),  # uploads/nombre desde backend
            os.path.join('uploads', nombre),
            os.path.join('backend', 'uploads', nombre),
            os.path.join('static', 'uploads', nombre),
        ]
        
        print(f"DEBUG: Rutas que se van a probar:")
        for i, ruta in enumerate(posibles_rutas, 1):
            abs_ruta = os.path.abspath(ruta)
            existe = os.path.exists(ruta)
            print(f"  {i}. {ruta}")
            print(f"     Absoluta: {abs_ruta}")
            print(f"     Existe: {existe}")
            if existe:
                print(f"DEBUG: ✅ LOGO CLIENTE ENCONTRADO EN: {ruta}")
                return ruta
        
        print(f"DEBUG: ❌ NO SE ENCONTRÓ EL LOGO CLIENTE: {cliente.logo_url}")
        return None
    
    def convertir_logo_a_html(self, logo_path, alt_text):
        """Convertir logo a HTML con data URI"""
        print(f"=== DEBUG CONVERTIR LOGO A HTML ===")
        print(f"DEBUG: Logo path: '{logo_path}'")
        print(f"DEBUG: Alt text: '{alt_text}'")
        
        if not logo_path:
            print("DEBUG: No hay logo_path, retornando placeholder")
            return f'<div class="logo-placeholder">{alt_text}</div>'
        
        if not os.path.exists(logo_path):
            print(f"DEBUG: El archivo NO existe: {logo_path}")
            return f'<div class="logo-placeholder">{alt_text}</div>'
        
        print(f"DEBUG: El archivo existe, convirtiendo a base64...")
        try:
            import base64
            
            # Determinar el tipo MIME basado en la extensión
            ext = os.path.splitext(logo_path)[1].lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.jfif': 'image/jpeg',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }
            mime_type = mime_types.get(ext, 'image/png')  # Default a PNG
            print(f"DEBUG: Extensión: {ext}, MIME type: {mime_type}")
            
            with open(logo_path, 'rb') as f:
                logo_data = base64.b64encode(f.read()).decode()
                print(f"DEBUG: Logo convertido a base64, longitud: {len(logo_data)}")
                return f'<img src="data:{mime_type};base64,{logo_data}" alt="{alt_text}" class="logo-image">'
        except Exception as e:
            print(f"DEBUG: ❌ ERROR convirtiendo logo {logo_path}: {e}")
            import traceback
            traceback.print_exc()
            return f'<div class="logo-placeholder">{alt_text}</div>'
    
    def convertir_foto_a_html(self, foto_path):
        """Convertir foto a HTML con data URI"""
        print(f"=== DEBUG CONVERTIR FOTO A HTML ===")
        print(f"DEBUG: Foto path: '{foto_path}'")
        
        if not foto_path:
            print("DEBUG: No hay foto_path, retornando placeholder")
            return '<div class="activity-photo-placeholder">Sin evidencia</div>'
        
        if not os.path.exists(foto_path):
            print(f"DEBUG: El archivo NO existe: {foto_path}")
            return '<div class="activity-photo-placeholder">Sin evidencia</div>'
        
        print(f"DEBUG: El archivo existe, convirtiendo a base64...")
        try:
            import base64
            
            # Determinar el tipo MIME basado en la extensión
            ext = os.path.splitext(foto_path)[1].lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.jfif': 'image/jpeg',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')  # Default a JPEG
            print(f"DEBUG: Extensión: {ext}, MIME type: {mime_type}")
            
            with open(foto_path, 'rb') as f:
                foto_data = base64.b64encode(f.read()).decode()
                print(f"DEBUG: Foto convertida a base64, longitud: {len(foto_data)}")
                return f'<img src="data:{mime_type};base64,{foto_data}" alt="Evidencia" class="activity-photo-image">'
        except Exception as e:
            print(f"DEBUG: ❌ ERROR convirtiendo foto {foto_path}: {e}")
            import traceback
            traceback.print_exc()
            return '<div class="activity-photo-placeholder">Error</div>'
    
    def generar_pdf(self, visita_id):
        try:
            print(f"=== INICIANDO GENERACIÓN HTML PDF PARA VISITA {visita_id} ===")
            print(f"DEBUG: Upload folder configurado: {self.upload_folder}")
            
            # Obtener datos de la visita
            visita = Visita.query.get(visita_id)
            if not visita:
                raise Exception(f"Visita {visita_id} no encontrada")
            
            print(f"DEBUG: Visita encontrada: {visita.id}")
            
            # Obtener zonas de la visita
            zonas = Zona.query.filter_by(visita_id=visita.id).all()
            print(f"DEBUG: Se encontraron {len(zonas)} zonas para la visita {visita_id}")
            
            # Obtener empresa (asociada al supervisor)
            supervisor = User.query.get(visita.supervisor_id)
            empresa = None
            if supervisor:
                empresa = Empresa.query.filter_by(user_id=supervisor.id).first()
                if not empresa:
                    empresa = Empresa.query.first()
            
            print(f"DEBUG: Empresa encontrada: {empresa.nombre if empresa else 'No encontrada'}")
            
            # Preparar datos para la plantilla
            template_data = {
                # Información básica
                'visita_id': str(visita.id),
                'fecha_visita': visita.fecha.strftime('%d/%m/%Y'),
                'supervisor_nombre': visita.supervisor.nombre[:20] + ('...' if len(visita.supervisor.nombre) > 20 else ''),
                'hora_visita': visita.hora.strftime('%H:%M') if visita.hora else visita.fecha.strftime('%H:%M'),
                'codigo_visita': visita.cliente.tipo_codigo[:8] if visita.cliente.tipo_codigo else 'N/A',
                
                # Información del cliente
                'cliente_nombre': visita.cliente.nombre[:20] + ('...' if len(visita.cliente.nombre) > 20 else ''),
                'cliente_nit': visita.cliente.nit[:15] + ('...' if len(visita.cliente.nit) > 15 else ''),
                'cliente_admin': visita.cliente.administrador[:18] + ('...' if len(visita.cliente.administrador) > 18 else ''),
                'cliente_email': visita.cliente.correo[:30] + ('...' if len(visita.cliente.correo) > 30 else ''),
                
                # Logos (convertir a HTML)
                'company_logo': self.convertir_logo_a_html(self.obtener_logo_empresa(empresa), "Logo Empresa"),
                'client_logo': self.convertir_logo_a_html(self.obtener_logo_cliente(visita.cliente), "Logo Cliente"),
                
                # Información de la empresa
                'company_name': empresa.nombre if empresa else 'Empresa',
                'company_address': empresa.direccion if empresa and empresa.direccion else 'Dirección no disponible',
                'company_nit': empresa.nit if empresa and empresa.nit else 'NIT no disponible',
                
                # Actividades por sección
                'actividades_aseo': self.obtener_actividades_por_seccion(zonas, 'Aseo y Limpieza'),
                'actividades_seguridad': self.obtener_actividades_por_seccion(zonas, 'Seguridad y Salud'),
                'actividades_colaborador': self.obtener_actividades_por_seccion(zonas, 'Colaborador'),
                
                # Conclusiones
                'conclusiones': self.limpiar_html(visita.conclusiones) if visita.conclusiones else None
            }
            
            print(f"DEBUG: Actividades aseo: {len(template_data['actividades_aseo'])}")
            print(f"DEBUG: Actividades seguridad: {len(template_data['actividades_seguridad'])}")
            print(f"DEBUG: Actividades colaborador: {len(template_data['actividades_colaborador'])}")
            
            # Debug de logos generados
            company_logo_preview = template_data['company_logo'][:100] if template_data['company_logo'] else 'None'
            client_logo_preview = template_data['client_logo'][:100] if template_data['client_logo'] else 'None'
            print(f"DEBUG: Company logo HTML (primeros 100 chars): {company_logo_preview}...")
            print(f"DEBUG: Client logo HTML (primeros 100 chars): {client_logo_preview}...")
            
            # Cargar y renderizar plantilla
            template = self.jinja_env.get_template('informe_template.html')
            html_content = template.render(**template_data)
            
            # Generar nombre del archivo PDF
            timestamp = datetime.now().strftime('%d%m%Y')
            filename = f"informe_{timestamp}-{visita_id}.pdf"
            filepath = os.path.join(self.upload_folder, filename)
            
            # Crear directorio si no existe
            os.makedirs(self.upload_folder, exist_ok=True)
            
            # Generar PDF con WeasyPrint
            print(f"DEBUG: Generando PDF en: {filepath}")
            html_doc = HTML(string=html_content)
            html_doc.write_pdf(filepath, stylesheets=[self.css])
            
            print(f"✅ PDF generado exitosamente: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error generando PDF: {str(e)}")
            raise e
