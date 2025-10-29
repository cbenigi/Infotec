#!/usr/bin/env python3
"""
Script para inicializar la base de datos en Railway
"""
import os
import sys
from werkzeug.security import generate_password_hash

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User

def init_database():
    """Inicializar la base de datos con datos básicos"""
    with app.app_context():
        try:
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas creadas correctamente")
            
            # Verificar si ya existe un admin
            admin_user = User.query.filter_by(email='cristianit@solamysas.com').first()
            
            if not admin_user:
                # Crear usuario admin
                admin_user = User(
                    nombre='Cristian',
                    email='cristianit@solamysas.com',
                    password_hash=generate_password_hash('123456789'),
                    rol='admin'
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Usuario admin creado: cristianit@solamysas.com")
            else:
                print("✅ Usuario admin ya existe")
            
            # Verificar que las tablas se crearon correctamente
            from models import Empresa, Cliente, Visita, Zona
            print("✅ Tablas verificadas:")
            print(f"   - Users: {User.query.count()} registros")
            print(f"   - Empresas: {Empresa.query.count()} registros")
            print(f"   - Clientes: {Cliente.query.count()} registros")
            print(f"   - Visitas: {Visita.query.count()} registros")
            print(f"   - Zonas: {Zona.query.count()} registros")
            
            print("🎉 Base de datos inicializada correctamente")
            
        except Exception as e:
            print(f"❌ Error inicializando base de datos: {e}")
            raise

if __name__ == '__main__':
    init_database()
