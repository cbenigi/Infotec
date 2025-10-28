#!/usr/bin/env python3
import os
import sys

from app import app
from models import User, Empresa, Cliente, Visita, Zona

def clean_database():
    with app.app_context():
        print("=== LIMPIANDO BASE DE DATOS ===\n")
        
        # Buscar usuario SOLAMY
        user = User.query.filter_by(email='solamy').first()
        if not user:
            print("❌ No se encontró usuario con email 'solamy'")
            return
        
        print(f"👤 Usuario encontrado: {user.email} (ID: {user.id})")
        
        # Obtener empresa del usuario
        empresa = Empresa.query.filter_by(user_id=user.id).first()
        if empresa:
            print(f"🏢 Empresa encontrada: {empresa.nombre} (ID: {empresa.id})")
        else:
            print("ℹ️  No hay empresa registrada para este usuario")
        
        # Obtener clientes
        clientes = Cliente.query.all()
        print(f"👥 Clientes encontrados: {len(clientes)}")
        for cliente in clientes:
            print(f"   - {cliente.nombre} (ID: {cliente.id})")
        
        # Obtener visitas
        visitas = Visita.query.all()
        print(f"📋 Visitas encontradas: {len(visitas)}")
        for visita in visitas:
            print(f"   - {visita.id} - {visita.cliente.nombre}")
        
        # Obtener zonas
        zonas = Zona.query.all()
        print(f"📍 Zonas encontradas: {len(zonas)}")
        
        # Confirmar eliminación
        print(f"\n⚠️  Se van a eliminar:")
        print(f"   - 1 usuario")
        print(f"   - {len(clientes)} clientes")
        print(f"   - {len(visitas)} visitas")
        print(f"   - {len(zonas)} zonas")
        if empresa:
            print(f"   - 1 empresa")
        
        confirm = input("\n¿Estás seguro? Escribe 'SI' para confirmar: ")
        if confirm != 'SI':
            print("❌ Operación cancelada")
            return
        
        # Eliminar en orden correcto (respetando foreign keys)
        print("\n🗑️  Eliminando datos...")
        
        # 1. Eliminar zonas (dependen de visitas)
        deleted_zonas = Zona.query.delete()
        print(f"   ✅ {deleted_zonas} zonas eliminadas")
        
        # 2. Eliminar visitas (dependen de clientes)
        deleted_visitas = Visita.query.delete()
        print(f"   ✅ {deleted_visitas} visitas eliminadas")
        
        # 3. Eliminar clientes
        deleted_clientes = Cliente.query.delete()
        print(f"   ✅ {deleted_clientes} clientes eliminados")
        
        # 4. Eliminar empresa (depende de usuario)
        if empresa:
            from app import db
            db.session.delete(empresa)
            print(f"   ✅ Empresa '{empresa.nombre}' eliminada")
        
        # 5. Eliminar usuario
        from app import db
        db.session.delete(user)
        print(f"   ✅ Usuario '{user.email}' eliminado")
        
        # Guardar cambios
        db.session.commit()
        
        print("\n✅ Base de datos limpiada exitosamente")
        
        # Verificar que se eliminó todo
        print("\n=== VERIFICACIÓN POST-LIMPIEZA ===")
        remaining_users = User.query.count()
        remaining_empresas = Empresa.query.count()
        remaining_clientes = Cliente.query.count()
        remaining_visitas = Visita.query.count()
        remaining_zonas = Zona.query.count()
        
        print(f"Usuarios restantes: {remaining_users}")
        print(f"Empresas restantes: {remaining_empresas}")
        print(f"Clientes restantes: {remaining_clientes}")
        print(f"Visitas restantes: {remaining_visitas}")
        print(f"Zonas restantes: {remaining_zonas}")

if __name__ == "__main__":
    clean_database()
