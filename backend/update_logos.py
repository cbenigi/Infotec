#!/usr/bin/env python3
import os
import sys

from app import app
from models import Empresa, Cliente

def update_logos():
    with app.app_context():
        print("=== ACTUALIZANDO LOGOS EN LA BASE DE DATOS ===\n")
        
        # Actualizar empresa
        empresa = Empresa.query.first()
        if empresa:
            empresa.logo_url = '/uploads/WhatsApp_Image_2025-10-22_at_10.24.22_AM.jpeg'
            print(f"Empresa '{empresa.nombre}' actualizada con logo: {empresa.logo_url}")
        else:
            print("No hay empresa registrada")
        
        # Actualizar cliente
        cliente = Cliente.query.first()
        if cliente:
            cliente.logo_url = '/uploads/WhatsApp_Image_2025-10-22_at_8.58.47_AM.jpeg'
            print(f"Cliente '{cliente.nombre}' actualizado con logo: {cliente.logo_url}")
        else:
            print("No hay cliente registrado")
        
        # Guardar cambios
        from app import db
        db.session.commit()
        print("\n✅ Cambios guardados en la base de datos")
        
        # Verificar que se guardaron
        print("\n=== VERIFICACIÓN POST-ACTUALIZACIÓN ===")
        empresa_updated = Empresa.query.first()
        cliente_updated = Cliente.query.first()
        
        if empresa_updated:
            print(f"Empresa logo_url: {empresa_updated.logo_url}")
        if cliente_updated:
            print(f"Cliente logo_url: {cliente_updated.logo_url}")

if __name__ == "__main__":
    update_logos()
