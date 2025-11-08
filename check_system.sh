#!/bin/bash

echo "🔍 VERIFICANDO SISTEMA SIESE..."
echo "================================"

# Verificar entorno virtual
if [ -d "siese_env" ]; then
    echo "✅ Entorno virtual encontrado"
    source siese_env/bin/activate
else
    echo "❌ Entorno virtual no encontrado"
    exit 1
fi

# Verificar Django
echo "📋 Verificando Django..."
python -c "import django; print(f'✅ Django {django.get_version()}')"

# Verificar base de datos
echo "🗃️ Verificando conexión a base de datos..."
python manage.py check --database default

# Verificar modelos
echo "📊 Verificando modelos..."
python manage.py check

# Verificar migraciones
echo "🔄 Verificando migraciones..."
python manage.py showmigrations

# Verificar datos iniciales
echo "📍 Verificando datos de ubicaciones..."
python manage.py shell -c "from apps.simulator.models import Location; print(f'✅ {Location.objects.count()} ciudades cargadas')"

# Verificar archivos estáticos
echo "📁 Verificando archivos estáticos..."
python manage.py findstatic admin/css/base.css --verbosity=0

# Verificar templates
echo "🎨 Verificando templates..."
if [ -f "templates/base.html" ]; then
    echo "✅ Template base encontrado"
else
    echo "❌ Template base no encontrado"
fi

# Resumen final
echo ""
echo "🎉 VERIFICACIÓN COMPLETADA"
echo "========================="
echo "🌐 Servidor: python manage.py runserver 8001"
echo "🔧 Admin: /admin/ (admin@siese.co / qwerty123)"
echo "📊 Apps: core, accounts, simulator, monitoring, educational, regulatory, news"
echo "🎨 Frontend: Tailwind CSS configurado"
echo "🗃️ Base de datos: MariaDB en puerto 3310"
echo ""
echo "¡Sistema listo para desarrollo personalizado! 🚀"
