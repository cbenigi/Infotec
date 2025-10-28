#!/usr/bin/env python3
import os
import sys

from app import app
from models import Empresa, Cliente

def check_logos():
    with app.app_context():
        print("=== VERIFICANDO LOGOS EN LA BASE DE DATOS ===\n")
        
        # Verificar empresas
        empresas = Empresa.query.all()
        print("EMPRESAS:")
        if empresas:
            for empresa in empresas:
                print(f"  ID: {empresa.id}")
                print(f"  Nombre: {empresa.nombre}")
                print(f"  Logo URL: {empresa.logo_url}")
                print(f"  Existe logo_url: {bool(empresa.logo_url)}")
                print("  ---")
        else:
            print("  No hay empresas registradas")
        
        print("\nCLIENTES:")
        clientes = Cliente.query.all()
        if clientes:
            for cliente in clientes:
                print(f"  ID: {cliente.id}")
                print(f"  Nombre: {cliente.nombre}")
                print(f"  Logo URL: {cliente.logo_url}")
                print(f"  Existe logo_url: {bool(cliente.logo_url)}")
                print("  ---")
        else:
            print("  No hay clientes registrados")
        
        print("\n=== VERIFICANDO ARCHIVOS DE LOGOS ===\n")
        
        # Verificar si existen archivos en uploads
        upload_dirs = ['uploads', 'backend/uploads', 'static/uploads']
        for upload_dir in upload_dirs:
            if os.path.exists(upload_dir):
                print(f"Directorio {upload_dir} existe:")
                files = os.listdir(upload_dir)
                if files:
                    for file in files:
                        print(f"  - {file}")
                else:
                    print("  (vacío)")
            else:
                print(f"Directorio {upload_dir} NO existe")

if __name__ == "__main__":
    check_logos()
