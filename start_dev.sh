#!/bin/bash

echo "🚀 INICIANDO DESARROLLO SIESE..."
echo "================================"

# Verificar entorno virtual
if [ -d "siese_env" ]; then
    echo "✅ Activando entorno virtual..."
    source siese_env/bin/activate
else
    echo "❌ Entorno virtual no encontrado. Ejecute setup primero."
    exit 1
fi

# Verificar conexión a base de datos
echo "�️ Verificando conexión a base de datos..."
python manage.py check --database default
if [ $? -ne 0 ]; then
    echo "❌ Error de conexión a base de datos"
    exit 1
fi

# Aplicar migraciones
echo "🔄 Aplicando migraciones..."
python manage.py migrate

# Cargar datos iniciales si no existen
echo "📍 Verificando datos de ubicaciones..."
LOCATIONS_COUNT=$(python manage.py shell -c "from apps.simulator.models import Location; print(Location.objects.count())" 2>/dev/null | tail -n 1)
if [ "$LOCATIONS_COUNT" -eq 0 ]; then
    echo "📦 Cargando ubicaciones de Colombia..."
    python manage.py load_locations
fi

# Verificar y actualizar Ley 1715 si ya está registrada
echo "⚖️ Verificando datos de Ley 1715..."
LEY_COUNT=$(python manage.py shell -c "from apps.regulatory.models import LegalFramework; print(LegalFramework.objects.filter(document_type='ley', document_number='1715', year=2014).count())" 2>/dev/null | tail -n 1)
if [ "$LEY_COUNT" -eq 0 ]; then
    echo "⚠️ No existe un registro de la Ley 1715 en la base de datos. Crea el registro desde el CRUD para poder actualizarlo."
else
    echo "🔄 Actualizando información de Ley 1715 de 2014..."
    python manage.py load_legal_framework --document-type ley --document-number 1715 --year 2014
fi

# Recopilar archivos estáticos
echo "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Verificar superusuario
echo "👤 Verificando superusuario..."
SUPERUSER_COUNT=$(python manage.py shell -c "from apps.accounts.models import User; print(User.objects.filter(is_superuser=True).count())" 2>/dev/null | tail -n 1)
if [ "$SUPERUSER_COUNT" -eq 0 ]; then
    echo "🔧 Creando superusuario por defecto..."
    python manage.py shell -c "
from apps.accounts.models import User
User.objects.create_superuser(
    email='admin@siese.co',
    password='qwerty123',
    first_name='Administrador',
    last_name='SIESE'
)
print('✅ Superusuario creado: admin@siese.co / qwerty123')
"
fi

echo ""
echo "🎉 SISTEMA LISTO PARA DESARROLLO"
echo "==============================="
echo "🌐 Servidor: http://127.0.0.1:8001/"
echo "� Admin: http://127.0.0.1:8001/admin/"
echo "� Usuario: admin@siese.co"
echo "🔑 Password: qwerty123"
echo "⚖️ Ley 1715: http://127.0.0.1:8001/regulatory/marco-legal/ley/1715/2014/"
echo ""
echo "� Funcionalidades disponibles:"
echo "   ✓ Sistema de usuarios con roles"
echo "   ✓ Simulador solar (10 ciudades)"
echo "   ✓ Marco regulatorio (Ley 1715)"
echo "   ✓ Panel de administración"
echo "   ✓ Templates responsivos"
echo ""

# Iniciar servidor
echo "�🚀 Iniciando servidor en puerto 8001..."
python manage.py runserver 8001
