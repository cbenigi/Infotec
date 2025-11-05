import os
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from jinja2 import Environment, FileSystemLoader
from models import Cotizacion, CotizacionItem, Empresa
import re
from datetime import datetime

class HTMLCotizacionGenerator:
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
                margin: 15mm 20mm;
            }
            body {
                font-family: Arial, sans-serif;
                font-size: 11px;
                line-height: 1.5;
                color: #333;
            }
        ''', font_config=self.font_config)
    
    def obtener_logo_empresa(self, empresa):
        """Obtener la ruta del logo de la empresa"""
        if not empresa or not empresa.logo_url:
            return None
        
        nombre = empresa.logo_url.split('/')[-1]
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        posibles_rutas = [
            os.path.join(self.upload_folder, nombre),
            os.path.join(base_dir, 'uploads', nombre),
            os.path.join(base_dir, '..', 'uploads', nombre),
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                return ruta
        
        return None
    
    def convertir_logo_a_base64(self, ruta_logo):
        """Convertir logo a base64"""
        if not ruta_logo or not os.path.exists(ruta_logo):
            return None
        
        try:
            import base64
            with open(ruta_logo, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Detectar tipo de imagen
            ext = os.path.splitext(ruta_logo)[1].lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.webp': 'image/webp',
                '.gif': 'image/gif'
            }
            mime = mime_types.get(ext, 'image/png')
            
            return f"data:{mime};base64,{img_data}"
        except Exception as e:
            print(f"Error al convertir logo a base64: {str(e)}")
            return None
    
    def generar_pdf(self, cotizacion_id):
        """Generar PDF de cotización"""
        try:
            print(f"=== GENERANDO PDF DE COTIZACIÓN {cotizacion_id} ===")
            
            # Obtener cotización con relaciones
            cotizacion = Cotizacion.query.get(cotizacion_id)
            if not cotizacion:
                print(f"ERROR: Cotización {cotizacion_id} no encontrada")
                return None
            
            print(f"Cotización encontrada: ID {cotizacion.id}")
            
            # Obtener empresa
            empresa = cotizacion.empresa
            print(f"Empresa: {empresa.nombre if empresa else 'Sin empresa'}")
            
            # Obtener supervisor
            supervisor = cotizacion.supervisor
            print(f"Supervisor: {supervisor.nombre if supervisor else 'Sin supervisor'}")
            
            # Obtener items ordenados
            items = sorted(cotizacion.items, key=lambda x: x.orden)
            print(f"Total items: {len(items)}")
            
            # Preparar logo de la empresa
            logo_base64 = None
            if empresa and empresa.logo_url:
                ruta_logo = self.obtener_logo_empresa(empresa)
                if ruta_logo:
                    logo_base64 = self.convertir_logo_a_base64(ruta_logo)
                    print(f"Logo de empresa procesado: {'Sí' if logo_base64 else 'No'}")
            
            # Preparar datos para el template
            contexto = {
                'cotizacion': {
                    'id': cotizacion.id,
                    'fecha_creacion': cotizacion.fecha_creacion.strftime('%d/%m/%Y'),
                    'hora_creacion': cotizacion.fecha_creacion.strftime('%H:%M'),
                    'estado': cotizacion.estado,
                    'observaciones': cotizacion.observaciones or ''
                },
                'empresa': {
                    'nombre': empresa.nombre if empresa else '',
                    'nit': empresa.nit if empresa else '',
                    'telefono': empresa.telefono if empresa else '',
                    'correo': empresa.correo if empresa else '',
                    'direccion': empresa.direccion if empresa else '',
                    'logo_base64': logo_base64
                },
                'supervisor': {
                    'nombre': supervisor.nombre if supervisor else '',
                    'email': supervisor.email if supervisor else ''
                },
                'items': [{
                    'numero': idx + 1,
                    'producto_servicio': item.producto_servicio,
                    'cantidad': item.cantidad,
                    'uso': item.uso
                } for idx, item in enumerate(items)]
            }
            
            # Cargar template
            template = self.jinja_env.get_template('cotizacion_template.html')
            html_content = template.render(**contexto)
            
            # Generar PDF
            output_filename = f'cotizacion_{cotizacion.id}.pdf'
            output_path = os.path.join(self.upload_folder, output_filename)
            
            print(f"Generando PDF en: {output_path}")
            
            HTML(string=html_content).write_pdf(
                output_path,
                stylesheets=[self.css],
                font_config=self.font_config
            )
            
            print(f"PDF generado exitosamente: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"ERROR al generar PDF de cotización: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

