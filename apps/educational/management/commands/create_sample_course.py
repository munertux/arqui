"""
Comando para crear un curso de ejemplo completo con contenido estructurado
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.educational.course_models import (
    Course, Module, Slide, ModuleQuizQuestion, ModuleQuizOption,
    FinalExamQuestion, FinalExamOption
)
from apps.educational.models import Category
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Crea un curso completo de ejemplo sobre Fundamentos de Energía Solar'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creando curso de ejemplo...'))
        
        # Obtener o crear categoría
        category, _ = Category.objects.get_or_create(
            slug='energia-solar',
            defaults={
                'name': 'Energía Solar',
                'description': 'Recursos sobre energía solar fotovoltaica',
                'is_active': True
            }
        )
        
        # Obtener autor (primer superusuario o crear uno de prueba)
        author = User.objects.filter(is_superuser=True).first()
        if not author:
            author, _ = User.objects.get_or_create(
                email='admin@siese.com',
                defaults={
                    'first_name': 'Admin',
                    'last_name': 'SIESE',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
        
        # Crear curso
        course, created = Course.objects.get_or_create(
            slug='fundamentos-energia-solar',
            defaults={
                'title': 'Fundamentos de Energía Solar Fotovoltaica',
                'description': '''Este curso completo te introducirá al fascinante mundo de la energía solar 
                fotovoltaica. Aprenderás desde los conceptos básicos hasta aplicaciones prácticas, diseño 
                de sistemas y normativas colombianas. Ideal para estudiantes, profesionales y cualquier 
                persona interesada en energías renovables.''',
                'level': 'basic',
                'estimated_hours': 12.0,
                'author': author,
                'category': category,
                'final_pass_score': 75,
                'publish_state': 'published',
                'max_final_attempts': 3,
                'is_active': True
            }
        )
        
        if not created:
            self.stdout.write(self.style.WARNING('El curso ya existe, actualizando contenido...'))
            # Eliminar módulos, preguntas de examen para recrear
            course.modules.all().delete()
            course.final_questions.all().delete()
        
        # MÓDULO 1: Introducción a la energía solar
        mod1 = Module.objects.create(
            course=course,
            title='Introducción a la Energía Solar',
            order=1,
            summary='Conceptos fundamentales sobre energía solar y su importancia global',
            required_pass_score=70,
            is_active=True
        )
        
        Slide.objects.create(
            module=mod1, order=1, title='¿Qué es la energía solar?',
            subtitle='Fundamentos de la radiación solar',
            content_type='text',
            duration_minutes=5,
            content='''<h2>Energía Solar: La fuente del futuro</h2>
            <p>La energía solar es la energía obtenida a partir de la radiación electromagnética del Sol. 
            Es una fuente renovable, limpia e inagotable que puede transformarse en electricidad o calor.</p>
            <p>El Sol libera aproximadamente 3.8 x 10^26 vatios de energía cada segundo. 
            La Tierra recibe solo una pequeña fracción, pero es suficiente para abastecer 
            10,000 veces el consumo energético mundial actual.</p>''',
            key_points='''Energía limpia y renovable
El Sol produce energía mediante fusión nuclear
La Tierra recibe suficiente energía solar para abastecer al mundo entero
No genera emisiones de CO2''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod1, order=2, title='Historia de la energía fotovoltaica',
            subtitle='Evolución tecnológica',
            content_type='text',
            duration_minutes=6,
            content='''<h2>Cronología del desarrollo solar</h2>
            <ul>
                <li><strong>1839:</strong> Alexandre Edmond Becquerel descubre el efecto fotovoltaico</li>
                <li><strong>1954:</strong> Bell Labs desarrolla la primera celda solar de silicio (6% eficiencia)</li>
                <li><strong>1958:</strong> Primera aplicación espacial en el satélite Vanguard I</li>
                <li><strong>1970s:</strong> Crisis petrolera impulsa investigación en energías alternativas</li>
                <li><strong>2000-2020:</strong> Reducción de costos del 90% y eficiencias superiores al 22%</li>
                <li><strong>2025:</strong> Colombia alcanza 5 GW de capacidad instalada</li>
            </ul>''',
            key_points='''Descubrimiento en 1839 por Becquerel
Primera celda práctica en 1954
Aplicaciones espaciales impulsaron la tecnología
Costos han disminuido dramáticamente''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod1, order=3, title='El recurso solar en Colombia',
            subtitle='Potencial energético nacional',
            content_type='text',
            duration_minutes=7,
            content='''<h2>Colombia: Un país privilegiado</h2>
            <p>Colombia cuenta con una irradiación solar promedio de <strong>5.5 kWh/m2/día</strong>, 
            una de las más altas del mundo. Esto se debe a su ubicación ecuatorial.</p>
            
            <h3>Regiones con mayor potencial:</h3>
            <ul>
                <li><strong>La Guajira:</strong> 6.2 kWh/m2/día - Ideal para grandes proyectos</li>
                <li><strong>Norte de Santander:</strong> 5.8 kWh/m2/día</li>
                <li><strong>Cesar y Magdalena:</strong> 5.7 kWh/m2/día</li>
                <li><strong>Valle del Cauca:</strong> 4.8 kWh/m2/día</li>
            </ul>
            
            <p>Esta abundancia permite sistemas solares productivos durante todo el año.</p>''',
            key_points='''Irradiación promedio: 5.5 kWh/m2/día
La Guajira: región con mayor potencial (6.2 kWh/m2/día)
Ubicación ecuatorial favorece producción constante
Potencial para abastecer varias veces la demanda nacional''',
            additional_resources='IDEAM - Atlas de Radiación Solar de Colombia',
            is_active=True
        )
        
        # Quiz módulo 1
        q1_1 = ModuleQuizQuestion.objects.create(
            module=mod1,
            text='¿Qué es la energía solar fotovoltaica?',
            question_type='single',
            explanation='La energía solar fotovoltaica convierte luz solar directamente en electricidad mediante celdas semiconductoras.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q1_1, text='Energía que convierte luz solar en electricidad', is_correct=True)
        ModuleQuizOption.objects.create(question=q1_1, text='Energía que calienta agua con el sol', is_correct=False)
        ModuleQuizOption.objects.create(question=q1_1, text='Energía eólica', is_correct=False)
        
        q1_2 = ModuleQuizQuestion.objects.create(
            module=mod1,
            text='¿Cuál es la irradiación solar promedio en Colombia?',
            question_type='single',
            explanation='Colombia tiene una irradiación promedio de 5.5 kWh/m2/día, siendo La Guajira la región con mayor potencial.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q1_2, text='5.5 kWh/m2/día', is_correct=True)
        ModuleQuizOption.objects.create(question=q1_2, text='2.5 kWh/m2/día', is_correct=False)
        ModuleQuizOption.objects.create(question=q1_2, text='8.0 kWh/m2/día', is_correct=False)
        
        # MÓDULO 2: Tecnología fotovoltaica
        mod2 = Module.objects.create(
            course=course,
            title='Tecnología Fotovoltaica',
            order=2,
            summary='Componentes y funcionamiento de sistemas fotovoltaicos',
            required_pass_score=70,
            is_active=True
        )
        
        Slide.objects.create(
            module=mod2, order=1, title='El efecto fotovoltaico',
            subtitle='Física detrás de las celdas solares',
            content_type='text',
            duration_minutes=8,
            content='''<h2>¿Cómo funciona una celda solar?</h2>
            <p>El efecto fotovoltaico es el fenómeno físico por el cual ciertos materiales 
            (semiconductores) generan electricidad cuando son expuestos a la luz.</p>
            
            <h3>Proceso paso a paso:</h3>
            <ol>
                <li><strong>Absorción de fotones:</strong> La luz solar contiene fotones con energía</li>
                <li><strong>Excitación de electrones:</strong> Los fotones liberan electrones en el material semiconductor</li>
                <li><strong>Separación de cargas:</strong> Campo eléctrico interno separa electrones y huecos</li>
                <li><strong>Flujo de corriente:</strong> Los electrones fluyen a través de un circuito externo</li>
            </ol>
            
            <p>Este proceso ocurre sin partes móviles, emisiones ni ruido.</p>''',
            key_points='''Fotones de luz liberan electrones en semiconductores
Campo eléctrico interno separa las cargas
Flujo de electrones genera corriente eléctrica
Proceso silencioso y sin emisiones''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod2, order=2, title='Tipos de paneles solares',
            subtitle='Monocristalino, policristalino y capa fina',
            content_type='text',
            duration_minutes=10,
            content='''<h2>Principales tecnologías de paneles</h2>
            
            <h3>1. Monocristalino (Mono-Si)</h3>
            <ul>
                <li>Eficiencia: 18-22%</li>
                <li>Color negro uniforme</li>
                <li>Mayor costo pero mayor rendimiento</li>
                <li>Ideal para espacios limitados</li>
            </ul>
            
            <h3>2. Policristalino (Poly-Si)</h3>
            <ul>
                <li>Eficiencia: 15-17%</li>
                <li>Color azul con patrón cristalino visible</li>
                <li>Menor costo</li>
                <li>Buena relación costo-beneficio</li>
            </ul>
            
            <h3>3. Capa fina (Thin-Film)</h3>
            <ul>
                <li>Eficiencia: 10-13%</li>
                <li>Flexible y ligero</li>
                <li>Mejor desempeño en sombra parcial</li>
                <li>Requiere más espacio</li>
            </ul>''',
            key_points='''Monocristalino: máxima eficiencia (18-22%)
Policristalino: mejor relación costo-beneficio (15-17%)
Capa fina: flexible pero menos eficiente (10-13%)
Selección depende de espacio y presupuesto''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod2, order=3, title='Componentes de un sistema fotovoltaico',
            subtitle='Más allá de los paneles',
            content_type='text',
            duration_minutes=9,
            content='''<h2>Sistema fotovoltaico completo</h2>
            
            <h3>1. Paneles solares (Módulos FV)</h3>
            <p>Convierten luz solar en electricidad DC</p>
            
            <h3>2. Inversor</h3>
            <p>Convierte corriente continua (DC) a alterna (AC) para uso doméstico/industrial</p>
            
            <h3>3. Estructura de montaje</h3>
            <p>Soporta paneles con ángulo e inclinación óptimos</p>
            
            <h3>4. Cableado y protecciones</h3>
            <p>Conduce electricidad de forma segura con fusibles, breakers y protección contra sobretensiones</p>
            
            <h3>5. Medidor bidireccional (opcional)</h3>
            <p>Mide energía consumida e inyectada a la red</p>
            
            <h3>6. Baterías (sistemas aislados)</h3>
            <p>Almacenan energía para uso nocturno o días nublados</p>''',
            key_points='''Paneles + Inversor = componentes principales
Estructura de montaje optimiza ángulo
Protecciones eléctricas son obligatorias
Baterías opcionales para sistemas aislados''',
            is_active=True
        )
        
        # Quiz módulo 2
        q2_1 = ModuleQuizQuestion.objects.create(
            module=mod2,
            text='¿Qué tipo de panel solar tiene la mayor eficiencia?',
            question_type='single',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q2_1, text='Monocristalino', is_correct=True)
        ModuleQuizOption.objects.create(question=q2_1, text='Policristalino', is_correct=False)
        ModuleQuizOption.objects.create(question=q2_1, text='Capa fina', is_correct=False)
        
        q2_2 = ModuleQuizQuestion.objects.create(
            module=mod2,
            text='¿Cuál es la función del inversor en un sistema fotovoltaico?',
            question_type='single',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q2_2, text='Convertir DC a AC', is_correct=True)
        ModuleQuizOption.objects.create(question=q2_2, text='Almacenar energía', is_correct=False)
        ModuleQuizOption.objects.create(question=q2_2, text='Medir consumo', is_correct=False)
        
        # MÓDULO 3: Diseño de sistemas
        mod3 = Module.objects.create(
            course=course,
            title='Diseño Básico de Sistemas Fotovoltaicos',
            order=3,
            summary='Cálculo de dimensionamiento y consideraciones de diseño',
            required_pass_score=75,
            is_active=True
        )
        
        Slide.objects.create(
            module=mod3, order=1, title='Análisis de consumo energético',
            subtitle='Primer paso en el diseño',
            content_type='text',
            duration_minutes=10,
            content='''<h2>Determinando tus necesidades</h2>
            <p>Antes de dimensionar un sistema solar, debemos conocer el consumo energético.</p>
            
            <h3>Pasos para calcular consumo:</h3>
            <ol>
                <li><strong>Inventario de cargas:</strong> Lista todos los equipos eléctricos</li>
                <li><strong>Potencia de cada equipo:</strong> En vatios (W)</li>
                <li><strong>Horas de uso diario:</strong> Tiempo de operación</li>
                <li><strong>Consumo diario:</strong> Potencia x Horas = Wh/día</li>
            </ol>
            
            <h3>Ejemplo práctico:</h3>
            <table border="1" cellpadding="5">
                <tr><th>Equipo</th><th>Potencia (W)</th><th>Horas/día</th><th>Consumo (Wh)</th></tr>
                <tr><td>Nevera</td><td>150</td><td>24</td><td>3,600</td></tr>
                <tr><td>Televisor LED</td><td>80</td><td>6</td><td>480</td></tr>
                <tr><td>Bombillas LED (5)</td><td>50</td><td>5</td><td>250</td></tr>
                <tr><td><strong>TOTAL</strong></td><td></td><td></td><td><strong>4,330 Wh/día</strong></td></tr>
            </table>''',
            key_points='''Inventario de cargas es fundamental
Consumo = Potencia x Horas de uso
Considerar picos de demanda
Agregar 20% de margen de seguridad''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod3, order=2, title='Dimensionamiento de paneles',
            subtitle='¿Cuántos paneles necesito?',
            content_type='text',
            duration_minutes=12,
            content='''<h2>Cálculo de paneles solares</h2>
            
            <h3>Fórmula básica:</h3>
            <p><strong>Número de paneles = Consumo diario (Wh) / (HSP x Potencia panel x Eficiencia sistema)</strong></p>
            
            <h3>Variables:</h3>
            <ul>
                <li><strong>HSP (Horas Sol Pico):</strong> Promedio diario de irradiación (Colombia: 4.5-6 horas)</li>
                <li><strong>Potencia del panel:</strong> Típicamente 250-400W</li>
                <li><strong>Eficiencia del sistema:</strong> 0.75-0.85 (pérdidas en cableado, inversor, temperatura)</li>
            </ul>
            
            <h3>Ejemplo con consumo de 4,330 Wh/día:</h3>
            <p>Ubicación: Bogotá (HSP = 4.5 horas)<br>
            Panel: 350W<br>
            Eficiencia: 0.80</p>
            
            <p><strong>Paneles = 4,330 / (4.5 x 350 x 0.80) = 4,330 / 1,260 aprox 3.4  a  4 paneles</strong></p>
            
            <p>Sistema recomendado: 4 paneles de 350W = 1,400W (1.4 kWp)</p>''',
            key_points='''HSP varía según ubicación geográfica
Considerar eficiencia del sistema (75-85%)
Redondear hacia arriba en número de paneles
Verificar espacio disponible''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod3, order=3, title='Selección del inversor',
            subtitle='Corazón del sistema',
            content_type='text',
            duration_minutes=8,
            content='''<h2>Eligiendo el inversor adecuado</h2>
            
            <h3>Tipos de inversores:</h3>
            <ul>
                <li><strong>String (cadena):</strong> Más económico, conecta varios paneles en serie</li>
                <li><strong>Microinversor:</strong> Uno por panel, mejor en sombras parciales</li>
                <li><strong>Optimizadores de potencia:</strong> Híbrido entre ambos</li>
            </ul>
            
            <h3>Criterios de selección:</h3>
            <ol>
                <li><strong>Potencia nominal:</strong> 90-110% de la potencia pico del arreglo</li>
                <li><strong>Rango de voltaje MPPT:</strong> Compatible con configuración de paneles</li>
                <li><strong>Eficiencia:</strong> >95% en inversores modernos</li>
                <li><strong>Garantía:</strong> Mínimo 10 años</li>
                <li><strong>Monitoreo:</strong> App móvil para seguimiento</li>
            </ol>
            
            <p><strong>Para nuestro ejemplo (1.4 kWp):</strong> Inversor de 1.5 kW</p>''',
            key_points='''Potencia inversor aprox 100% potencia pico
Eficiencia >95% es estándar
Verificar rango MPPT compatible
Monitoreo remoto es muy útil''',
            is_active=True
        )
        
        # Quiz módulo 3
        q3_1 = ModuleQuizQuestion.objects.create(
            module=mod3,
            text='¿Qué significa HSP en el diseño solar?',
            question_type='single',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q3_1, text='Horas Sol Pico', is_correct=True)
        ModuleQuizOption.objects.create(question=q3_1, text='Horas de Servicio del Panel', is_correct=False)
        ModuleQuizOption.objects.create(question=q3_1, text='Horas Sin Producción', is_correct=False)
        
        q3_2 = ModuleQuizQuestion.objects.create(
            module=mod3,
            text='En un sistema de 1.4 kWp, ¿qué potencia de inversor se recomienda?',
            question_type='single',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q3_2, text='1.5 kW', is_correct=True)
        ModuleQuizOption.objects.create(question=q3_2, text='1.0 kW', is_correct=False)
        ModuleQuizOption.objects.create(question=q3_2, text='2.5 kW', is_correct=False)
        
        # MÓDULO 4: Instalación y mantenimiento
        mod4 = Module.objects.create(
            course=course,
            title='Instalación y Mantenimiento',
            order=4,
            summary='Buenas prácticas de instalación y cuidado del sistema',
            required_pass_score=70,
            is_active=True
        )
        
        Slide.objects.create(
            module=mod4, order=1, title='Ubicación e inclinación de paneles',
            subtitle='Optimizando la captación solar',
            content_type='text',
            duration_minutes=8,
            content='''<h2>Posicionamiento óptimo</h2>
            
            <h3>Orientación:</h3>
            <p>En Colombia (hemisferio norte del ecuador), los paneles deben orientarse:</p>
            <ul>
                <li><strong>Norte geográfico:</strong> Para latitudes cerca al ecuador</li>
                <li><strong>Desviación máxima aceptable:</strong> ±15° con pérdidas <5%</li>
            </ul>
            
            <h3>Inclinación (ángulo de tilt):</h3>
            <p>Regla general: <strong>Inclinación = Latitud del lugar</strong></p>
            <ul>
                <li>Bogotá (4.7°N): 5-10°</li>
                <li>Medellín (6.2°N): 6-12°</li>
                <li>La Guajira (11.5°N): 11-15°</li>
            </ul>
            
            <h3>Consideraciones:</h3>
            <ul>
                <li>Evitar sombras de árboles, edificios o chimeneas</li>
                <li>Mínimo 10° para autolimpieza con lluvia</li>
                <li>Espacio entre filas para evitar sombreado mutuo</li>
            </ul>''',
            key_points='''Orientación norte para Colombia
Inclinación aprox latitud del lugar
Evitar sombras a toda costa
Mínimo 10° para drenaje de agua''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod4, order=2, title='Proceso de instalación',
            subtitle='Paso a paso',
            content_type='text',
            duration_minutes=10,
            content='''<h2>Secuencia de instalación</h2>
            
            <h3>1. Preparación del sitio</h3>
            <ul>
                <li>Inspección estructural del techo</li>
                <li>Verificar capacidad de carga</li>
                <li>Identificar paso de cables</li>
            </ul>
            
            <h3>2. Montaje de estructura</h3>
            <ul>
                <li>Anclaje seguro al techo (tornillos, abrazaderas)</li>
                <li>Impermeabilización de perforaciones</li>
                <li>Nivelación y alineación</li>
            </ul>
            
            <h3>3. Instalación de paneles</h3>
            <ul>
                <li>Montaje en rieles con grapas</li>
                <li>Conexión en serie/paralelo según diseño</li>
                <li>Uso de conectores MC4</li>
            </ul>
            
            <h3>4. Cableado eléctrico</h3>
            <ul>
                <li>Cables solares certificados (uso exterior)</li>
                <li>Canalización protegida</li>
                <li>String box con fusibles</li>
            </ul>
            
            <h3>5. Conexión del inversor</h3>
            <ul>
                <li>Montaje en lugar ventilado y protegido</li>
                <li>Conexión DC desde paneles</li>
                <li>Conexión AC al tablero eléctrico</li>
            </ul>
            
            <h3>6. Puesta en marcha</h3>
            <ul>
                <li>Verificación de polaridad</li>
                <li>Pruebas de funcionamiento</li>
                <li>Configuración de monitoreo</li>
            </ul>''',
            key_points='''Inspección estructural previa es crítica
Impermeabilización para evitar filtraciones
Cableado debe ser para uso solar (UV-resistente)
Pruebas completas antes de operar''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod4, order=3, title='Mantenimiento preventivo',
            subtitle='Garantizando 25+ años de operación',
            content_type='text',
            duration_minutes=7,
            content='''<h2>Cuidado del sistema solar</h2>
            
            <h3>Mantenimiento de paneles:</h3>
            <ul>
                <li><strong>Limpieza:</strong> Cada 6 meses o según acumulación de polvo</li>
                <li><strong>Inspección visual:</strong> Buscar microfisuras, decoloración</li>
                <li><strong>Verificar sombras:</strong> Crecimiento de vegetación cercana</li>
            </ul>
            
            <h3>Revisión de inversor:</h3>
            <ul>
                <li>Monitoreo de rendimiento (comparar con esperado)</li>
                <li>Verificar mensajes de error en pantalla</li>
                <li>Limpieza de ventilación</li>
            </ul>
            
            <h3>Sistema eléctrico:</h3>
            <ul>
                <li>Inspeccionar conexiones (oxidación, apriete)</li>
                <li>Verificar protecciones (fusibles, breakers)</li>
                <li>Medición de voltaje y corriente</li>
            </ul>
            
            <h3>Frecuencia recomendada:</h3>
            <ul>
                <li><strong>Mensual:</strong> Revisión visual + monitoreo remoto</li>
                <li><strong>Semestral:</strong> Limpieza de paneles</li>
                <li><strong>Anual:</strong> Inspección técnica completa</li>
            </ul>
            
            <p><strong>Importante:</strong> Trabajos en altura y eléctricos deben hacerse por personal capacitado.</p>''',
            key_points='''Limpieza semestral de paneles
Monitoreo continuo de rendimiento
Revisión anual técnica profesional
Seguridad primero: no DIY en altura''',
            is_active=True
        )
        
        # Quiz módulo 4
        q4_1 = ModuleQuizQuestion.objects.create(
            module=mod4,
            text='¿Cuál es la regla general para la inclinación de paneles en Colombia?',
            question_type='single',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q4_1, text='Inclinación igual a la latitud del lugar', is_correct=True)
        ModuleQuizOption.objects.create(question=q4_1, text='Siempre 45 grados', is_correct=False)
        ModuleQuizOption.objects.create(question=q4_1, text='Completamente horizontal', is_correct=False)
        
        q4_2 = ModuleQuizQuestion.objects.create(
            module=mod4,
            text='¿Con qué frecuencia se recomienda limpiar los paneles solares?',
            question_type='single',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q4_2, text='Cada 6 meses', is_correct=True)
        ModuleQuizOption.objects.create(question=q4_2, text='Cada semana', is_correct=False)
        ModuleQuizOption.objects.create(question=q4_2, text='Nunca, la lluvia los limpia', is_correct=False)
        
        # MÓDULO 5: Normativa y aspectos financieros
        mod5 = Module.objects.create(
            course=course,
            title='Normativa y Aspectos Financieros en Colombia',
            order=5,
            summary='Marco legal, incentivos y análisis económico',
            required_pass_score=75,
            is_active=True
        )
        
        Slide.objects.create(
            module=mod5, order=1, title='Marco normativo colombiano',
            subtitle='Leyes y regulaciones',
            content_type='text',
            duration_minutes=10,
            content='''<h2>Legislación de energías renovables</h2>
            
            <h3>Ley 1715 de 2014</h3>
            <p>Ley marco que promueve el desarrollo de fuentes no convencionales de energía renovable (FNCER).</p>
            
            <h3>Beneficios tributarios:</h3>
            <ul>
                <li><strong>Exención de IVA:</strong> Equipos y servicios para proyectos solares</li>
                <li><strong>Deducción de renta:</strong> 50% de la inversión en 15 años</li>
                <li><strong>Depreciación acelerada:</strong> Amortización en 5 años</li>
                <li><strong>Exención de aranceles:</strong> Importación de equipos certificados</li>
            </ul>
            
            <h3>Resolución CREG 030 de 2018</h3>
            <p>Regula la autogeneración a pequeña escala:</p>
            <ul>
                <li>Sistemas hasta 1 MW</li>
                <li>Medición neta (net metering)</li>
                <li>Inyección de excedentes a la red</li>
            </ul>
            
            <h3>RETIE (Reglamento Técnico de Instalaciones Eléctricas)</h3>
            <p>Normas de seguridad obligatorias para instalaciones eléctricas, incluyendo sistemas solares.</p>''',
            key_points='''Ley 1715/2014: marco legal principal
Incentivos tributarios significativos (IVA, renta, aranceles)
CREG 030/2018: autogeneración y net metering
RETIE: cumplimiento obligatorio de seguridad''',
            additional_resources='UPME - Unidad de Planeación Minero Energética',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod5, order=2, title='Análisis de retorno de inversión',
            subtitle='Viabilidad económica',
            content_type='text',
            duration_minutes=12,
            content='''<h2>¿Cuánto tarda en pagarse un sistema solar?</h2>
            
            <h3>Costos típicos en Colombia (2025):</h3>
            <ul>
                <li><strong>Sistema residencial (3-5 kWp):</strong> $15-20 millones COP</li>
                <li><strong>Costo por kWp:</strong> $3-4 millones COP</li>
                <li><strong>Incluye:</strong> Paneles, inversor, estructura, instalación</li>
            </ul>
            
            <h3>Ahorros mensuales:</h3>
            <p>Ejemplo sistema 4 kWp en Bogotá:</p>
            <ul>
                <li>Generación mensual: ~480 kWh</li>
                <li>Tarifa promedio: $600 COP/kWh</li>
                <li><strong>Ahorro mensual: $288,000 COP</strong></li>
                <li><strong>Ahorro anual: $3.45 millones COP</strong></li>
            </ul>
            
            <h3>Período de retorno:</h3>
            <p>Inversión inicial: $16 millones<br>
            Ahorro anual: $3.45 millones<br>
            <strong>Payback: 4.6 años</strong></p>
            
            <h3>Valor de vida útil (25 años):</h3>
            <ul>
                <li>Ahorro total: $86.25 millones</li>
                <li>Retorno sobre inversión: 539%</li>
                <li>Incremento valor de la propiedad</li>
            </ul>
            
            <p><em>Nota: Cálculos no incluyen incentivos fiscales que reducirían aún más el payback.</em></p>''',
            key_points='''Costo promedio: $3-4 millones/kWp
Período de retorno típico: 4-6 años
Vida útil de 25+ años genera ahorros significativos
Incrementa el valor de la propiedad''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod5, order=3, title='Trámites y certificaciones',
            subtitle='Proceso administrativo',
            content_type='text',
            duration_minutes=8,
            content='''<h2>Pasos para legalizar tu sistema solar</h2>
            
            <h3>1. Registro UPME</h3>
            <p>Inscripción del proyecto en el Registro de Proyectos de Generación con FNCER.</p>
            
            <h3>2. Certificación RETIE</h3>
            <ul>
                <li>Diseño por profesional certificado</li>
                <li>Instalación cumpliendo normativa</li>
                <li>Dictamen de inspección</li>
            </ul>
            
            <h3>3. Solicitud a operador de red</h3>
            <ul>
                <li>Formulario de conexión</li>
                <li>Planos y especificaciones</li>
                <li>Certificado RETIE</li>
            </ul>
            
            <h3>4. Instalación de medidor bidireccional</h3>
            <p>El operador instala contador que registra consumo e inyección.</p>
            
            <h3>5. Puesta en servicio</h3>
            <ul>
                <li>Aprobación final</li>
                <li>Inicio de generación y compensación</li>
            </ul>
            
            <h3>Tiempo total del proceso:</h3>
            <p>Entre 2-4 meses desde la solicitud inicial.</p>
            
            <h3>Certificaciones de producto:</h3>
            <ul>
                <li>IEC 61215 (paneles)</li>
                <li>IEC 62109 (inversores)</li>
                <li>Certificación RETIQ</li>
            </ul>''',
            key_points='''Registro UPME es el primer paso
Certificación RETIE obligatoria
Operador de red instala medidor bidireccional
Proceso toma 2-4 meses''',
            is_active=True
        )
        
        # Quiz módulo 5
        q5_1 = ModuleQuizQuestion.objects.create(
            module=mod5,
            text='Seleccione los beneficios tributarios de la Ley 1715 (múltiple respuesta):',
            question_type='multiple',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q5_1, text='Exención de IVA', is_correct=True)
        ModuleQuizOption.objects.create(question=q5_1, text='Deducción del 50% en renta', is_correct=True)
        ModuleQuizOption.objects.create(question=q5_1, text='Subsidio directo del 100%', is_correct=False)
        ModuleQuizOption.objects.create(question=q5_1, text='Depreciación acelerada', is_correct=True)
        
        q5_2 = ModuleQuizQuestion.objects.create(
            module=mod5,
            text='¿Cuál es el período típico de retorno de inversión para un sistema residencial en Colombia?',
            question_type='single',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q5_2, text='4-6 años', is_correct=True)
        ModuleQuizOption.objects.create(question=q5_2, text='15-20 años', is_correct=False)
        ModuleQuizOption.objects.create(question=q5_2, text='1-2 años', is_correct=False)
        
        # EXAMEN FINAL
        self.stdout.write(self.style.SUCCESS('Creando preguntas de examen final...'))
        
        ef1 = FinalExamQuestion.objects.create(
            course=course,
            text='¿Qué porcentaje aproximado de la energía mundial podría suplirse con la radiación solar que recibe la Tierra?',
            question_type='single',
            is_active=True
        )
        FinalExamOption.objects.create(question=ef1, text='10,000 veces el consumo actual', is_correct=True)
        FinalExamOption.objects.create(question=ef1, text='10% del consumo actual', is_correct=False)
        FinalExamOption.objects.create(question=ef1, text='Exactamente el consumo actual', is_correct=False)
        
        ef2 = FinalExamQuestion.objects.create(
            course=course,
            text='¿Cuál es la irradiación solar promedio en La Guajira, Colombia?',
            question_type='single',
            is_active=True
        )
        FinalExamOption.objects.create(question=ef2, text='6.2 kWh/m2/día', is_correct=True)
        FinalExamOption.objects.create(question=ef2, text='3.5 kWh/m2/día', is_correct=False)
        FinalExamOption.objects.create(question=ef2, text='8.0 kWh/m2/día', is_correct=False)
        
        ef3 = FinalExamQuestion.objects.create(
            course=course,
            text='¿Qué tipo de panel solar ofrece la mejor relación costo-beneficio?',
            question_type='single',
            is_active=True
        )
        FinalExamOption.objects.create(question=ef3, text='Policristalino', is_correct=True)
        FinalExamOption.objects.create(question=ef3, text='Monocristalino', is_correct=False)
        FinalExamOption.objects.create(question=ef3, text='Capa fina', is_correct=False)
        
        ef4 = FinalExamQuestion.objects.create(
            course=course,
            text='¿Cuál es la función principal del inversor en un sistema fotovoltaico?',
            question_type='single',
            is_active=True
        )
        FinalExamOption.objects.create(question=ef4, text='Convertir corriente continua (DC) a alterna (AC)', is_correct=True)
        FinalExamOption.objects.create(question=ef4, text='Almacenar energía para la noche', is_correct=False)
        FinalExamOption.objects.create(question=ef4, text='Regular la temperatura de los paneles', is_correct=False)
        
        ef5 = FinalExamQuestion.objects.create(
            course=course,
            text='Para un consumo diario de 5,000 Wh con HSP de 5 horas, paneles de 400W y eficiencia 0.80, ¿cuántos paneles se necesitan aproximadamente?',
            question_type='single',
            is_active=True
        )
        FinalExamOption.objects.create(question=ef5, text='4 paneles', is_correct=True)
        FinalExamOption.objects.create(question=ef5, text='2 paneles', is_correct=False)
        FinalExamOption.objects.create(question=ef5, text='8 paneles', is_correct=False)
        
        ef6 = FinalExamQuestion.objects.create(
            course=course,
            text='Seleccione los componentes esenciales de un sistema fotovoltaico conectado a red (múltiple):',
            question_type='multiple',
            is_active=True
        )
        FinalExamOption.objects.create(question=ef6, text='Paneles solares', is_correct=True)
        FinalExamOption.objects.create(question=ef6, text='Inversor', is_correct=True)
        FinalExamOption.objects.create(question=ef6, text='Baterías', is_correct=False)
        FinalExamOption.objects.create(question=ef6, text='Estructura de montaje', is_correct=True)
        
        ef7 = FinalExamQuestion.objects.create(
            course=course,
            text='¿Cuál debe ser la orientación de los paneles solares en Colombia?',
            question_type='single',
            is_active=True
        )
        FinalExamOption.objects.create(question=ef7, text='Norte geográfico', is_correct=True)
        FinalExamOption.objects.create(question=ef7, text='Sur geográfico', is_correct=False)
        FinalExamOption.objects.create(question=ef7, text='Este-oeste', is_correct=False)
        
        ef8 = FinalExamQuestion.objects.create(
            course=course,
            text='¿Con qué frecuencia se debe realizar limpieza de paneles solares?',
            question_type='single',
            is_active=True
        )
        FinalExamOption.objects.create(question=ef8, text='Cada 6 meses', is_correct=True)
        FinalExamOption.objects.create(question=ef8, text='Cada mes', is_correct=False)
        FinalExamOption.objects.create(question=ef8, text='Nunca', is_correct=False)
        
        ef9 = FinalExamQuestion.objects.create(
            course=course,
            text='¿Qué normativa colombiana establece los incentivos tributarios para energía solar?',
            question_type='single',
            is_active=True
        )
        FinalExamOption.objects.create(question=ef9, text='Ley 1715 de 2014', is_correct=True)
        FinalExamOption.objects.create(question=ef9, text='Ley 142 de 1994', is_correct=False)
        FinalExamOption.objects.create(question=ef9, text='Decreto 2041', is_correct=False)
        
        ef10 = FinalExamQuestion.objects.create(
            course=course,
            text='¿Cuál es el período típico de retorno de inversión de un sistema solar residencial en Colombia?',
            question_type='single',
            is_active=True
        )
        FinalExamOption.objects.create(question=ef10, text='4-6 años', is_correct=True)
        FinalExamOption.objects.create(question=ef10, text='10-15 años', is_correct=False)
        FinalExamOption.objects.create(question=ef10, text='1-2 años', is_correct=False)
        
        self.stdout.write(self.style.SUCCESS(f'''
        ✅ Curso creado exitosamente: "{course.title}"
        
        📊 Resumen:
        - 5 módulos temáticos
        - {Slide.objects.filter(module__course=course).count()} diapositivas detalladas
        - {ModuleQuizQuestion.objects.filter(module__course=course).count()} preguntas de quiz
        - {FinalExamQuestion.objects.filter(course=course).count()} preguntas de examen final
        
        🌐 Accede al curso en:
        http://127.0.0.1:8001/education/cursos/fundamentos-energia-solar/
        
        💡 Estructura del contenido:
        Módulo 1: Introducción (3 slides, 2 preguntas)
        Módulo 2: Tecnología (3 slides, 2 preguntas)
        Módulo 3: Diseño (3 slides, 2 preguntas)
        Módulo 4: Instalación (3 slides, 2 preguntas)
        Módulo 5: Normativa (3 slides, 2 preguntas)
        Examen final: 10 preguntas (75% para aprobar)
        '''))
