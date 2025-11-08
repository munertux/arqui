<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# SIESE - Instrucciones para GitHub Copilot

## Contexto del Proyecto

SIESE es un Sistema Integral de Energía Solar en Colombia, desarrollado como una aplicación web con Django. El objetivo es proporcionar herramientas para la simulación, monitoreo y aprendizaje sobre energía solar.

## Arquitectura y Tecnologías

- **Backend**: Django 5.0.6 con arquitectura modular por apps
- **Frontend**: Tailwind CSS con componentes personalizados
- **Base de datos**: MariaDB (puerto 3310)
- **Autenticación**: Django Allauth con sistema de roles
- **API**: Django REST Framework
- **Tareas asíncronas**: Celery + Redis
- **Estilos**: Tailwind CSS + Font Awesome

## Estructura de Apps

1. **core**: Funcionalidades base, modelos abstractos
2. **accounts**: Sistema de usuarios con roles (Editor/Cliente)
3. **simulator**: Simulador de sistemas solares
4. **monitoring**: Panel de monitoreo y métricas
5. **educational**: Recursos educativos
6. **regulatory**: Repositorio normativo
7. **news**: Sistema de noticias y blog

## Patrones de Desarrollo

### Modelos
- Usar `BaseModel` como clase base para todos los modelos
- Implementar `__str__` descriptivos
- Usar `verbose_name` y `help_text` en los campos
- Seguir convenciones de nomenclatura en español para el usuario final

### Vistas
- Preferir Class-Based Views (CBV)
- Implementar mixins para autenticación y permisos
- Documentar las vistas con docstrings

### Templates
- Extender desde `base.html`
- Usar Tailwind CSS para estilos
- Implementar responsive design
- Usar iconos de Font Awesome con prefijo `fas fa-`

### URLs
- Usar `app_name` en cada URLconf
- Nombres de URL descriptivos y consistentes
- Agrupar URLs por funcionalidad

## Convenciones de Código

### Python/Django
- Seguir PEP 8
- Usar type hints cuando sea apropiado
- Documentar funciones complejas
- Manejar excepciones apropiadamente

### HTML/CSS
- Usar clases de Tailwind CSS
- Mantener consistencia en colores del tema:
  - `colombia-blue`: #003A70
  - `solar-yellow`: #FFD700
  - `solar-orange`: #FF8C00
  - `earth-green`: #228B22

### JavaScript
- Usar ES6+ cuando sea posible
- Mantener código modular y reutilizable
- Documentar funciones complejas

## Sistema de Roles

- **Editor**: Puede crear, editar y publicar contenido
- **Cliente/Usuario**: Acceso a panel personal y funciones básicas
- **Público**: Acceso a contenido de divulgación sin autenticación

## Mejores Prácticas

1. **Seguridad**: Validar entrada de usuarios, usar CSRF tokens
2. **Performance**: Optimizar consultas, usar paginación
3. **UX**: Interfaces intuitivas, mensajes claros de error/éxito
4. **Accesibilidad**: Usar semantic HTML, alt text en imágenes
5. **SEO**: Meta tags apropiados, URLs amigables

## Contexto de Colombia

- Usar formato de fecha DD/MM/YYYY
- Moneda en pesos colombianos (COP)
- Zona horaria: America/Bogota
- Idioma: Español colombiano
- Considerar diversidad geográfica del país

## Datos de Energía Solar

- Promedio de irradiación: 5.5 kWh/m²/día
- Factores climáticos regionales
- Normativas energéticas colombianas
- Incentivos fiscales y tributarios

## Testing

- Escribir tests para modelos, vistas y formularios
- Usar fixtures para datos de prueba
- Testear tanto casos exitosos como de error

## API Guidelines

- Seguir principios REST
- Usar serializers de DRF
- Implementar paginación
- Documentar endpoints claramente

Cuando generes código para SIESE, considera estos patrones y convenciones para mantener consistencia y calidad en el proyecto.
