import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from models import OrdenCompra, Empresa, Proveedor, User, Cliente
from html_pdf_generator import HTMLPDFGenerator

class HTMLOrdenGenerator:
    def __init__(self, upload_folder=None):
        base_dir = os.path.dirname(__file__)
        self.template_dir = os.path.join(base_dir, 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(self.template_dir))
        self.upload_folder = upload_folder or os.environ.get('UPLOAD_FOLDER', '/app/uploads')
        self.font_config = FontConfiguration()
        self.css = CSS(string='''
            @page {
                size: A4;
                margin: 12mm 15mm;
            }
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                color: #222;
            }
        ''', font_config=self.font_config)
        self.logo_helper = HTMLPDFGenerator(upload_folder=self.upload_folder)

    def _format_currency(self, value):
        if value is None:
            return '$ 0'
        return "$ {:,.0f}".format(value).replace(',', '.')

    def generar_pdf(self, orden_id):
        orden = OrdenCompra.query.get_or_404(orden_id)
        supervisor = User.query.get(orden.supervisor_id)
        empresa = orden.empresa or (Empresa.query.filter_by(user_id=supervisor.id).first() if supervisor else None)
        proveedor = orden.proveedor if orden.proveedor_id else None

        template = self.jinja_env.get_template('orden_compra_template.html')

        items = sorted(orden.items, key=lambda x: x.posicion)
        item_rows = []
        for idx, item in enumerate(items, start=1):
            cantidad = item.cantidad
            try:
                cantidad_val = float(str(cantidad).replace(',', '.'))
            except (ValueError, TypeError):
                cantidad_val = None
            subtotal = None
            if cantidad_val is not None and item.precio_unitario:
                subtotal = cantidad_val * item.precio_unitario
            item_rows.append({
                'index': idx,
                'descripcion': item.descripcion,
                'cantidad': cantidad,
                'unidad': item.unidad,
                'precio_unitario': self._format_currency(item.precio_unitario) if item.precio_unitario else '—',
                'subtotal': self._format_currency(subtotal) if subtotal is not None else '—',
                'comentarios': item.comentarios
            })

        company_logo = self.logo_helper.convertir_logo_a_html(
            self.logo_helper.obtener_logo_empresa(empresa),
            "Logo Empresa"
        ) if empresa else None

        if orden.comprador_tipo == 'cliente':
            comprador = Cliente.query.get(orden.comprador_id)
            comprador_nombre = comprador.nombre if comprador else 'Cliente'
        else:
            comprador = empresa
            comprador_nombre = empresa.nombre if empresa else 'Empresa'

        proveedor_direccion = orden.proveedor_direccion or (proveedor.direccion if proveedor and proveedor.direccion else '')
        proveedor_insumos = orden.proveedor_tipo_insumos or (proveedor.tipo_insumos if proveedor and proveedor.tipo_insumos else '')

        template_data = {
            'orden': orden,
            'empresa': empresa,
            'proveedor': proveedor,
            'supervisor': supervisor,
            'items': item_rows,
            'company_logo': company_logo or '',
            'fecha_emision': orden.fecha_creacion.strftime('%d/%m/%Y'),
            'fecha_entrega': orden.fecha_entrega.strftime('%d/%m/%Y') if orden.fecha_entrega else 'Pendiente',
            'subtotal': self._format_currency(orden.subtotal),
            'iva': self._format_currency(orden.iva_valor),
            'total': self._format_currency(orden.total),
            'iva_porcentaje': '19%',
            'comprador_nombre': comprador_nombre,
            'proveedor_direccion': proveedor_direccion or '—',
            'proveedor_insumos': proveedor_insumos or '—'
        }

        html_content = template.render(**template_data)

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"orden_compra_{orden.numero}_{timestamp}.pdf"
        filepath = os.path.join(self.upload_folder, filename)
        os.makedirs(self.upload_folder, exist_ok=True)

        HTML(string=html_content).write_pdf(filepath, stylesheets=[self.css])
        return filepath

