# SIESE - Sistema Integral de Energía Solar en Colombia

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0.6-green.svg)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0+-38B2AC.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌞 Descripción

SIESE es una plataforma web integral para la simulación, monitoreo y aprendizaje sobre energía solar en Colombia. El sistema permite a usuarios y editores acceder a herramientas especializadas para la transición hacia energías renovables.

## 📋 Características Principales

### 🔧 Módulos del Sistema

- **Simulador Solar**: Calcula producción y ahorro estimado basado en ubicación y parámetros del sistema
- **Monitoreo y Ahorro**: Panel con métricas (kWh, CO₂ evitado, ahorros económicos) y visualizaciones históricas
- **Recursos Educativos**: Artículos, guías y materiales formativos sobre energía solar
- **Repositorio Normativo**: Consulta y búsqueda de normas y lineamientos del sector
- **Posteo/Noticias**: Publicaciones y actualizaciones del proyecto

### 👥 Sistema de Autenticación

- **Rol Editor**: Acceso a sección de posteo/gestión de contenidos (crear, editar, publicar)
- **Rol Cliente/Usuario**: Panel de monitoreo y contenidos personalizados
- **Sección Pública**: Contenido de divulgación sin necesidad de login

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.0.6, Django REST Framework
- **Frontend**: Tailwind CSS, HTML5, JavaScript
- **Base de Datos**: MariaDB (Puerto 3310)
- **Autenticación**: Django Allauth
- **Tareas Asíncronas**: Celery + Redis
- **Estilos**: Tailwind CSS con componentes personalizados
- **Formularios**: Django Crispy Forms con Tailwind

## 🏗️ Arquitectura del Proyecto

```
siese/
├── apps/
│   ├── core/           # Funcionalidades base
│   ├── accounts/       # Sistema de usuarios y autenticación
│   ├── simulator/      # Simulador solar
│   ├── monitoring/     # Monitoreo y métricas
│   ├── educational/    # Recursos educativos
│   ├── regulatory/     # Repositorio normativo
│   └── news/          # Noticias y posteos
├── templates/         # Templates HTML
├── static/           # Archivos estáticos (CSS, JS, imágenes)
├── media/           # Archivos subidos por usuarios
├── logs/            # Archivos de log
└── requirements.txt # Dependencias Python
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8 o superior
- MariaDB/MySQL
- Redis (para Celery)
- Git

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd siese
```

### 2. Crear Entorno Virtual

```bash
python3 -m venv siese_env
source siese_env/bin/activate  # Linux/Mac
# o
siese_env\Scripts\activate     # Windows
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear archivo `.env` en el directorio raíz:

```env
# Variables de entorno
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos
DB_NAME=test_arqui
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3310

# Email (configurar para producción)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Redis (para Celery)
REDIS_URL=redis://localhost:6379/0

# Archivos estáticos
STATIC_ROOT=staticfiles
MEDIA_ROOT=media
```

### 5. Configurar Base de Datos

```bash
# Crear base de datos en MariaDB
mysql -u root -p -e "CREATE DATABASE test_arqui CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 7. Ejecutar el Servidor

```bash
python manage.py runserver
```

El sitio estará disponible en: `http://127.0.0.1:8000`

## 🎨 Configuración de Tailwind CSS

El proyecto utiliza Tailwind CSS vía CDN para desarrollo. Para producción, se recomienda instalar Tailwind CSS localmente:

```bash
# Instalar Node.js y npm primero
npm init -y
npm install -D tailwindcss
npx tailwindcss init

# Configurar build de CSS
npm run build-css
```

## 📊 Configuración de Celery (Opcional)

Para tareas asíncronas como envío de emails y generación de reportes:

```bash
# Terminal 1: Ejecutar worker de Celery
celery -A siese worker --loglevel=info

# Terminal 2: Ejecutar beat de Celery (tareas programadas)
celery -A siese beat --loglevel=info
```

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
python manage.py test

# Ejecutar pruebas de una app específica
python manage.py test apps.simulator

# Ejecutar con coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 📝 API Documentation

El proyecto incluye Django REST Framework. La documentación de la API estará disponible en:

- API Root: `http://127.0.0.1:8000/api/v1/`
- Admin Panel: `http://127.0.0.1:8000/admin/`

## 🏭 Despliegue en Producción

### Variables de Entorno para Producción

```env
DEBUG=False
SECRET_KEY=clave-super-secreta-y-unica
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Base de datos de producción
DB_NAME=siese_prod
DB_USER=siese_user
DB_PASSWORD=contraseña-segura
DB_HOST=tu-servidor-db
DB_PORT=3306

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.tu-proveedor.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@dominio.com
EMAIL_HOST_PASSWORD=tu-contraseña
```

### Comandos de Despliegue

```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Ejecutar migraciones
python manage.py migrate

# Usar Gunicorn como servidor WSGI
gunicorn siese.wsgi:application --bind 0.0.0.0:8000
```

## 📂 Estructura de Apps

### Core
- Modelos base y funcionalidades comunes
- Vistas principales del sitio
- Configuraciones globales

### Accounts
- Modelo de usuario personalizado
- Autenticación con roles (Editor/Cliente)
- Perfiles de usuario

### Simulator
- Modelos: Location, SolarSystem, Simulation
- Cálculos de producción solar
- Estimaciones de ahorro

### Monitoring
- Lecturas de energía
- Reportes mensuales
- Dashboard de métricas

### Educational
- Recursos educativos categorizados
- Sistema de categorías
- Contador de visualizaciones

### Regulatory
- Documentos regulatorios
- Sistema de búsqueda
- Categorización por tipo de documento

### News
- Sistema de noticias y blog
- Editor de contenido para usuarios con rol Editor
- Categorización y etiquetado

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Contacto

- Email: info@siese.co
- Teléfono: +57 (1) 123-4567
- Dirección: Bogotá, Colombia

## 🔮 Roadmap

- [ ] Implementar API REST completa
- [ ] Integración con sistemas de monitoreo IoT
- [ ] Dashboard avanzado con visualizaciones interactivas
- [ ] Sistema de notificaciones push
- [ ] App móvil complementaria
- [ ] Integración con proveedores de equipos
- [ ] Sistema de cotizaciones automáticas
- [ ] Mapas de radiación solar interactivos
