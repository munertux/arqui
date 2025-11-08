#!/usr/bin/env python
"""
Script para crear superusuario inicial
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siese.settings')
django.setup()

from apps.accounts.models import User

def create_superuser():
    try:
        if not User.objects.filter(email='admin@siese.co').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@siese.co',
                password='qwerty123',
                first_name='Admin',
                last_name='SIESE',
                role='editor'
            )
            print("✅ Superusuario creado exitosamente:")
            print("   Email: admin@siese.co")
            print("   Password: qwerty123")
            print("   Rol: Editor")
        else:
            print("⚠️  Superusuario ya existe")
    except Exception as e:
        print(f"❌ Error al crear superusuario: {e}")

if __name__ == "__main__":
    create_superuser()
