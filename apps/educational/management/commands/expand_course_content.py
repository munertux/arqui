"""
Script para EXPANDIR el curso existente con mucho más contenido por módulo
Ejecutar con: python manage.py expand_course_content
"""
from django.core.management.base import BaseCommand
from django.db import models
from apps.educational.course_models import Course, Module, Slide, ModuleQuizQuestion, ModuleQuizOption


class Command(BaseCommand):
    help = 'Expande el curso Fundamentos de Energía Solar con más slides y preguntas'

    def handle(self, *args, **kwargs):
        try:
            course = Course.objects.get(slug='fundamentos-energia-solar')
        except Course.DoesNotExist:
            self.stdout.write(self.style.ERROR('Curso no encontrado. Ejecuta primero create_sample_course'))
            return

        self.stdout.write(self.style.SUCCESS('Expandiendo curso con más contenido...'))
        
        # Obtener módulos existentes
        modules = course.modules.all().order_by('order')
        
        for module in modules:
            current_slides = module.slides.count()
            current_questions = module.questions.count()
            
            # Saltar módulos ya expandidos (más de 4 slides)
            if current_slides > 4:
                self.stdout.write(self.style.WARNING(
                    f'Módulo {module.order} ya expandido ({current_slides} slides), saltando...'
                ))
                continue
            
            if module.order == 1:  # Introducción
                self.expand_module_1(module)
            elif module.order == 2:  # Tecnología
                self.expand_module_2(module)
            elif module.order == 3:  # Diseño
                self.expand_module_3(module)
            elif module.order == 4:  # Instalación
                self.expand_module_4(module)
            elif module.order == 5:  # Normativa
                self.expand_module_5(module)
            
            new_slides = module.slides.count()
            new_questions = module.questions.count()
            
            self.stdout.write(self.style.SUCCESS(
                f'Módulo {module.order}: {current_slides} a {new_slides} slides, '
                f'{current_questions} a {new_questions} preguntas'
            ))
        
        self.stdout.write(self.style.SUCCESS('\n[CORRECTO] Curso expandido exitosamente!'))
        self.stdout.write(f'Total slides: {Slide.objects.filter(module__course=course).count()}')
        self.stdout.write(f'Total preguntas: {ModuleQuizQuestion.objects.filter(module__course=course).count()}')

    def expand_module_1(self, mod1):
        """Expande Módulo 1: Introducción - de 3 a 7 slides, de 2 a 6 preguntas"""
        max_order = mod1.slides.aggregate(models.Max('order'))['order__max'] or 0
        
        # Agregar slides adicionales
        Slide.objects.create(
            module=mod1, order=max_order + 1,
            title='El espectro electromagnético solar',
            subtitle='Composición de la luz solar',
            content_type='text',
            duration_minutes=7,
            content='''<h2>¿De qué está compuesta la luz solar?</h2>
            <p>La radiación solar que llega a la Tierra está compuesta por diferentes longitudes de onda:</p>
            <ul>
                <li><strong>Ultravioleta (UV):</strong> 7% - Longitud de onda menor a 400 nm</li>
                <li><strong>Luz visible:</strong> 47% - Entre 400-700 nm (lo que vemos con los ojos)</li>
                <li><strong>Infrarrojo (IR):</strong> 46% - Mayor a 700 nm (calor)</li>
            </ul>
            <h3>Importancia para paneles solares:</h3>
            <p>Las celdas de silicio aprovechan principalmente la luz visible y parte del infrarrojo cercano. 
            Cada material tiene un "band gap" que determina qué longitudes de onda puede absorber.</p>
            <h3>Estándar AM 1.5:</h3>
            <p>La industria usa el estándar AM 1.5 (Air Mass 1.5) que representa la radiación después de 
            atravesar 1.5 veces el espesor de la atmósfera. Es el estándar internacional para probar paneles.</p>''',
            key_points='''UV: 7%, Visible: 47%, IR: 46%
Celdas de silicio usan principalmente luz visible
AM 1.5: estándar internacional de pruebas
Band gap determina qué luz se absorbe''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod1, order=max_order + 2,
            title='Beneficios de la energía solar',
            subtitle='Ventajas ambientales, económicas y sociales',
            content_type='text',
            duration_minutes=8,
            content='''<h2>¿Por qué elegir energía solar?</h2>
            <h3>Beneficios ambientales:</h3>
            <ul>
                <li>Cero emisiones de CO2 en operación (sistema 5kW evita 3.5 ton/año)</li>
                <li>No consume agua (vs termoeléctricas)</li>
                <li>No genera contaminación del aire</li>
                <li>Preserva recursos fósiles</li>
            </ul>
            <h3>Beneficios económicos:</h3>
            <ul>
                <li>Reducción de factura eléctrica 50-100%</li>
                <li>Retorno de inversión: 4-7 años en Colombia</li>
                <li>Protección contra aumentos de tarifas</li>
                <li>Incrementa valor de propiedad 4-6%</li>
                <li>Incentivos fiscales disponibles</li>
            </ul>
            <h3>Beneficios sociales:</h3>
            <ul>
                <li>Independencia energética</li>
                <li>Genera 3x más empleos que combustibles fósiles</li>
                <li>Electrificación de zonas rurales</li>
                <li>Estabilidad de precios energéticos</li>
            </ul>''',
            key_points='''Sistema 5kW evita 3.5 ton CO2/año
ROI: 4-7 años en Colombia
Reduce factura 50-100%
No consume agua
Crea más empleos que fósiles''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod1, order=max_order + 3,
            title='Aplicaciones de la energía solar',
            subtitle='Usos residenciales, comerciales e industriales',
            content_type='text',
            duration_minutes=6,
            content='''<h2>¿Dónde se usa la energía solar?</h2>
            <h3>Solar Fotovoltaica (Electricidad):</h3>
            <ul>
                <li><strong>Residencial:</strong> Techos de casas (2-10 kWp)</li>
                <li><strong>Comercial:</strong> Edificios, bodegas (10-500 kWp)</li>
                <li><strong>Industrial:</strong> Fábricas (500kWp - 5MWp)</li>
                <li><strong>Utility-scale:</strong> Granjas solares mayores a 5MWp</li>
                <li><strong>Off-grid:</strong> Zonas sin red eléctrica</li>
            </ul>
            <h3>Solar Térmica (Calor):</h3>
            <ul>
                <li>Calentadores de agua domésticos</li>
                <li>Calefacción de piscinas</li>
                <li>Procesos industriales</li>
                <li>Cocción solar</li>
            </ul>
            <h3>Aplicaciones emergentes:</h3>
            <ul>
                <li>Vehículos eléctricos con carga solar</li>
                <li>Agrovoltaica (cultivos + paneles)</li>
                <li>Hidrógeno verde</li>
                <li>Desalinización de agua</li>
            </ul>''',
            key_points='''Residencial: 2-10 kWp
Comercial: 10-500 kWp
Industrial: >500 kWp
Off-grid: sin red eléctrica
Aplicaciones: FV, térmica, concentrada''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod1, order=max_order + 4,
            title='Energía solar en el mundo',
            subtitle='Líderes globales y tendencias',
            content_type='text',
            duration_minutes=7,
            content='''<h2>Panorama global de la energía solar</h2>
            <h3>Top 10 países por capacidad instalada (2025):</h3>
            <ol>
                <li><strong>China:</strong> 610 GW - Líder absoluto, 35% del total mundial</li>
                <li><strong>Estados Unidos:</strong> 180 GW - Crecimiento acelerado</li>
                <li><strong>India:</strong> 85 GW - Objetivo 500 GW para 2030</li>
                <li><strong>Japón:</strong> 78 GW - Densidad alta por área limitada</li>
                <li><strong>Alemania:</strong> 85 GW - Pionero europeo</li>
                <li><strong>Australia:</strong> 32 GW - Mayor penetración per cápita</li>
                <li><strong>España:</strong> 28 GW - Renacimiento solar</li>
                <li><strong>Brasil:</strong> 25 GW - Líder latinoamericano</li>
                <li><strong>Francia:</strong> 18 GW</li>
                <li><strong>Corea del Sur:</strong> 17 GW</li>
            </ol>
            <h3>Colombia:</h3>
            <p>Capacidad instalada: <strong>5 GW</strong> (2025)<br>
            Objetivo 2030: <strong>15 GW</strong><br>
            Crecimiento anual: ~35%</p>
            <h3>Tendencias globales:</h3>
            <ul>
                <li>1,500 GW de capacidad solar global total</li>
                <li>Solar es la energía más instalada anualmente</li>
                <li>Costos siguen bajando 10-15% por año</li>
                <li>Almacenamiento en baterías se vuelve estándar</li>
            </ul>''',
            key_points='''China: 610 GW (líder mundial)
Total global: ~1,500 GW
Colombia: 5 GW, meta 15 GW para 2030
Solar es la energía más instalada actualmente
Costos bajan 10-15% anualmente''',
            is_active=True
        )
        
        # Agregar más preguntas de quiz
        q = ModuleQuizQuestion.objects.create(
            module=mod1,
            text='¿Qué porcentaje del espectro solar corresponde a luz visible?',
            question_type='single',
            explanation='La luz visible es el 47% del espectro solar.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='47%', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='70%', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='25%', is_correct=False)
        
        q = ModuleQuizQuestion.objects.create(
            module=mod1,
            text='¿En qué año se desarrolló la primera celda solar de silicio práctica?',
            question_type='single',
            explanation='Bell Labs desarrolló la primera celda de silicio en 1954 con 6% de eficiencia.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='1954', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='1839', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='2000', is_correct=False)
        
        q = ModuleQuizQuestion.objects.create(
            module=mod1,
            text='Seleccione los beneficios ambientales de la energía solar (múltiple):',
            question_type='multiple',
            explanation='Solar no emite CO2 en operación, no consume agua y preserva recursos fósiles.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='Cero emisiones de CO2', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='No consume agua', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Genera residuos tóxicos', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='Preserva combustibles fósiles', is_correct=True)
        
        q = ModuleQuizQuestion.objects.create(
            module=mod1,
            text='¿Qué país lidera la capacidad solar instalada mundial?',
            question_type='single',
            explanation='China lidera con 610 GW, representando el 35% del total mundial.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='China', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Estados Unidos', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='Alemania', is_correct=False)

    def expand_module_2(self, mod2):
        """Expande Módulo 2: Tecnología - de 3 a 7 slides, de 2 a 6 preguntas"""
        max_order = mod2.slides.aggregate(models.Max('order'))['order__max'] or 0
        
        Slide.objects.create(
            module=mod2, order=max_order + 1,
            title='Tipos avanzados de celdas solares',
            subtitle='Tecnologías emergentes',
            content_type='text',
            duration_minutes=9,
            content='''<h2>Más allá del silicio convencional</h2>
            <h3>Celdas de Heterounión (HJT - Heterojunction):</h3>
            <ul>
                <li>Eficiencia: 24-26% en producción</li>
                <li>Combinan silicio cristalino con capa de silicio amorfo</li>
                <li>Mejor desempeño a altas temperaturas</li>
                <li>Fabricantes: REC, Panasonic, Meyer Burger</li>
            </ul>
            <h3>Celdas PERC (Passivated Emitter Rear Cell):</h3>
            <ul>
                <li>Eficiencia: 21-23%</li>
                <li>Capa reflectante en parte trasera aumenta absorción</li>
                <li>Tecnología más común actualmente</li>
                <li>Costo similar al mono estándar</li>
            </ul>
            <h3>Celdas TOPCon (Tunnel Oxide Passivated Contact):</h3>
            <ul>
                <li>Eficiencia: 23-25%</li>
                <li>Sucesora de PERC</li>
                <li>Menor degradación, vida útil >30 años</li>
            </ul>
            <h3>Perovskitas (Emergente):</h3>
            <ul>
                <li>Eficiencia lab: >33% (récord mundial)</li>
                <li>Bajo costo de fabricación</li>
                <li>Flexibles y ligeras</li>
                <li>Desafío: estabilidad a largo plazo</li>
            </ul>
            <h3>Tándem (Futuro):</h3>
            <ul>
                <li>Combinan perovskita + silicio</li>
                <li>Eficiencia potencial: >40%</li>
                <li>Aprovechan más del espectro solar</li>
            </ul>''',
            key_points='''HJT: 24-26% eficiencia, mejor en calor
PERC: tecnología dominante actual
TOPCon: sucesora de PERC, >30 años vida
Perovskitas: >33% en lab, bajo costo
Tándem: potencial >40% eficiencia''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod2, order=max_order + 2,
            title='Inversores: Tipos y características',
            subtitle='Comparativa detallada',
            content_type='text',
            duration_minutes=10,
            content='''<h2>Elegir el inversor correcto</h2>
            <h3>1. Inversores String (Cadena):</h3>
            <ul>
                <li><strong>Descripción:</strong> Múltiples paneles conectados en serie a un inversor central</li>
                <li><strong>Ventajas:</strong> Menor costo inicial, mantenimiento centralizado</li>
                <li><strong>Desventajas:</strong> Sombreado afecta toda la cadena</li>
                <li><strong>Aplicación:</strong> Techos sin sombras, sistemas residenciales/comerciales</li>
                <li><strong>Costo:</strong> $0.08-0.15/W</li>
            </ul>
            <h3>2. Microinversores:</h3>
            <ul>
                <li><strong>Descripción:</strong> Un inversor pequeño por cada panel</li>
                <li><strong>Ventajas:</strong> Optimización panel por panel, escalabilidad</li>
                <li><strong>Desventajas:</strong> Mayor costo inicial (+20-30%)</li>
                <li><strong>Aplicación:</strong> Techos complejos, sombreado parcial</li>
                <li><strong>Marcas:</strong> Enphase, APsystems</li>
            </ul>
            <h3>3. Optimizadores de Potencia + Inversor:</h3>
            <ul>
                <li><strong>Descripción:</strong> Optimizador DC en cada panel + inversor central</li>
                <li><strong>Ventajas:</strong> Optimización individual, monitoreo detallado</li>
                <li><strong>Desventajas:</strong> Costo medio</li>
                <li><strong>Marca líder:</strong> SolarEdge</li>
            </ul>
            <h3>4. Inversores Híbridos (con batería):</h3>
            <ul>
                <li><strong>Descripción:</strong> Gestionan paneles + baterías + red</li>
                <li><strong>Ventajas:</strong> Almacenamiento, respaldo</li>
                <li><strong>Desventajas:</strong> Mayor complejidad y costo</li>
                <li><strong>Marcas:</strong> Tesla, SolarEdge, Fronius</li>
            </ul>
            <h3>Criterios de selección:</h3>
            <ul>
                <li>Eficiencia: >96% (mínimo), >98% (ideal)</li>
                <li>Rango MPPT compatible con arreglo</li>
                <li>Garantía: 10-25 años</li>
                <li>Monitoreo WiFi incluido</li>
                <li>Certificaciones: IEC 62109, UL 1741</li>
            </ul>''',
            key_points='''String: más económico, sin sombras
Microinversores: panel por panel, +costo
Optimizadores: balance costo-beneficio
Híbridos: incluyen gestión baterías
Eficiencia >96% mínimo, >98% ideal''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod2, order=max_order + 3,
            title='Sistemas de almacenamiento',
            subtitle='Baterías para energía solar',
            content_type='text',
            duration_minutes=10,
            content='''<h2>Almacenar el Sol para la noche</h2>
            <h3>Tecnologías de baterías:</h3>
            
            <h4>1. Litio-Ion (Li-ion) - Estándar actual:</h4>
            <ul>
                <li><strong>Variantes:</strong> LFP (LiFePO4), NMC, NCA</li>
                <li><strong>Eficiencia:</strong> 90-95%</li>
                <li><strong>Ciclos de vida:</strong> 3,000-10,000</li>
                <li><strong>Profundidad de descarga:</strong> 80-100%</li>
                <li><strong>Costo:</strong> $300-600/kWh</li>
                <li><strong>Ventajas:</strong> Alta densidad, larga vida</li>
            </ul>
            
            <h4>2. Plomo-Ácido (tradicional):</h4>
            <ul>
                <li><strong>Tipos:</strong> AGM, Gel</li>
                <li><strong>Eficiencia:</strong> 70-85%</li>
                <li><strong>Ciclos:</strong> 500-2,000</li>
                <li><strong>DoD:</strong> 50% recomendado</li>
                <li><strong>Costo:</strong> $150-250/kWh</li>
                <li><strong>Desventaja:</strong> Requiere mantenimiento, vida corta</li>
            </ul>
            
            <h4>3. Flow Batteries (Flujo) - Emergente:</h4>
            <ul>
                <li>Escalabilidad independiente (potencia vs capacidad)</li>
                <li>Vida útil: >20,000 ciclos</li>
                <li>Costo alto inicial</li>
                <li>Ideal para proyectos grandes</li>
            </ul>
            
            <h3>Baterías populares residenciales:</h3>
            <ul>
                <li><strong>Tesla Powerwall 3:</strong> 13.5 kWh, $9,000 USD</li>
                <li><strong>LG RESU:</strong> 9.8-16 kWh</li>
                <li><strong>Sonnen eco:</strong> 5-15 kWh modular</li>
                <li><strong>BYD Battery-Box:</strong> 2.5-15.4 kWh</li>
            </ul>
            
            <h3>¿Cuándo vale la pena?</h3>
            <ul>
                <li>Zonas sin red eléctrica (off-grid)</li>
                <li>Tarifa diferencial horaria (TOU)</li>
                <li>Red inestable, apagones frecuentes</li>
                <li>Autosuficiencia energética deseada</li>
            </ul>
            
            <p><strong>Nota Colombia:</strong> Con medición neta actual, red actúa como "batería virtual" 
            sin costo adicional. Baterías físicas aún no son económicamente óptimas para on-grid.</p>''',
            key_points='''Li-ion: estándar actual, 3k-10k ciclos
LFP (LiFePO4): más segura, larga vida
Plomo: barato pero vida corta
Tesla Powerwall: 13.5 kWh, $9k
Baterías óptimas: off-grid o red inestable''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod2, order=max_order + 4,
            title='Estructuras de montaje',
            subtitle='Opciones según tipo de techo',
            content_type='text',
            duration_minutes=8,
            content='''<h2>Bases sólidas para tus paneles</h2>
            
            <h3>1. Techo inclinado (tejas):</h3>
            <ul>
                <li><strong>Sistema de rieles:</strong> Aluminio anodizado</li>
                <li><strong>Anclajes:</strong> Ganchos atornillados a estructura</li>
                <li><strong>Impermeabilización:</strong> Tapajuntas, sellantes</li>
                <li><strong>Ventaja:</strong> Ángulo pre-existente, drenaje natural</li>
                <li><strong>Peso adicional:</strong> 15-20 kg/m2</li>
            </ul>
            
            <h3>2. Techo plano (concreto):</h3>
            <ul>
                <li><strong>Sistemas:</strong> Lastrado o atornillado</li>
                <li><strong>Inclinación:</strong> 10-15grados típico</li>
                <li><strong>Ventaja:</strong> Sin perforaciones (lastrado)</li>
                <li><strong>Consideración:</strong> Carga de viento</li>
            </ul>
            
            <h3>3. Suelo (terreno):</h3>
            <ul>
                <li><strong>Cimentación:</strong> Concreto o pilotes</li>
                <li><strong>Altura:</strong> Mínimo 50cm del suelo</li>
                <li><strong>Ventaja:</strong> Fácil acceso, escalable</li>
                <li><strong>Desventaja:</strong> Uso de terreno</li>
            </ul>
            
            <h3>4. Tracker (seguimiento solar):</h3>
            <ul>
                <li><strong>Un eje:</strong> Sigue el Sol este-oeste</li>
                <li><strong>Dos ejes:</strong> Optimización total</li>
                <li><strong>Ganancia:</strong> 15-25% más energía</li>
                <li><strong>Costo:</strong> +40-60%</li>
                <li><strong>Aplicación:</strong> Solo proyectos grandes</li>
            </ul>
            
            <h3>Materiales comunes:</h3>
            <ul>
                <li><strong>Rieles:</strong> Aluminio 6063-T5</li>
                <li><strong>Grapas:</strong> Acero inoxidable 304/316</li>
                <li><strong>Tornillería:</strong> Acero galvanizado o inox</li>
                <li><strong>Vida útil:</strong> >25 años</li>
            </ul>
            
            <h3>Consideraciones de diseño:</h3>
            <ul>
                <li>Carga de viento según zona geográfica</li>
                <li>Espacio entre paneles para mantenimiento</li>
                <li>Evitar sombreado entre filas</li>
                <li>Accesibilidad para limpieza</li>
            </ul>''',
            key_points='''Techo inclinado: rieles + ganchos
Techo plano: lastrado o atornillado
Materiales: aluminio + inox
Trackers: +15-25% energía, +40-60% costo
Considerar carga de viento''',
            is_active=True
        )
        
        # Agregar preguntas
        q = ModuleQuizQuestion.objects.create(
            module=mod2,
            text='¿Qué tecnología de celda solar tiene actualmente la mayor eficiencia comercial?',
            question_type='single',
            explanation='Las celdas HJT (Heterounión) alcanzan 24-26% en producción comercial.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='HJT (Heterojunction)', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='PERC', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='Capa fina', is_correct=False)
        
        q = ModuleQuizQuestion.objects.create(
            module=mod2,
            text='¿Cuál es la eficiencia mínima aceptable en un inversor moderno?',
            question_type='single',
            explanation='Los inversores modernos deben tener al menos 96% de eficiencia, idealmente >98%.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='>96%', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='>85%', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='>75%', is_correct=False)
        
        q = ModuleQuizQuestion.objects.create(
            module=mod2,
            text='Seleccione las ventajas de los microinversores (múltiple):',
            question_type='multiple',
            explanation='Microinversores optimizan cada panel individualmente y son escalables fácilmente.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='Optimización panel por panel', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Fácil escalabilidad', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Menor costo inicial', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='Mejor con sombras parciales', is_correct=True)
        
        q = ModuleQuizQuestion.objects.create(
            module=mod2,
            text='¿Cuántos ciclos de vida tienen típicamente las baterías de Litio-Ion?',
            question_type='single',
            explanation='Las baterías Li-ion para solar tienen entre 3,000-10,000 ciclos dependiendo del modelo.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='3,000-10,000 ciclos', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='500-1,000 ciclos', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='20,000-30,000 ciclos', is_correct=False)

    def expand_module_3(self, mod3):
        """Expande Módulo 3: Diseño - de 3 a 6 slides, de 2 a 5 preguntas"""
        max_order = mod3.slides.aggregate(models.Max('order'))['order__max'] or 0
        
        Slide.objects.create(
            module=mod3, order=max_order + 1,
            title='Configuraciones de paneles: Serie vs Paralelo',
            subtitle='Optimizando voltaje y corriente',
            content_type='text',
            duration_minutes=9,
            content='''<h2>Cómo conectar tus paneles</h2>
            <h3>Conexión en Serie:</h3>
            <ul>
                <li><strong>Efecto:</strong> Suma voltajes, corriente constante</li>
                <li><strong>Ejemplo:</strong> 4 paneles x 40V = 160V, corriente = 10A</li>
                <li><strong>Ventajas:</strong> Menor pérdida en cables, inversores más pequeños</li>
                <li><strong>Desventajas:</strong> Sombra en un panel afecta toda la cadena</li>
                <li><strong>Aplicación:</strong> Techos uniformes sin sombras</li>
            </ul>
            <h3>Conexión en Paralelo:</h3>
            <ul>
                <li><strong>Efecto:</strong> Suma corrientes, voltaje constante</li>
                <li><strong>Ejemplo:</strong> 4 paneles x 10A = 40A, voltaje = 40V</li>
                <li><strong>Ventajas:</strong> Sombra afecta solo ese panel</li>
                <li><strong>Desventajas:</strong> Mayores pérdidas en cables, fusibles necesarios</li>
            </ul>
            <h3>Configuración Serie-Paralelo (Combinada):</h3>
            <ul>
                <li>Combina ventajas de ambas</li>
                <li>Ejemplo: 2 strings de 4 paneles en serie, conectados en paralelo</li>
                <li>Más común en sistemas medianos-grandes</li>
            </ul>
            <h3>Consideraciones:</h3>
            <ul>
                <li>Rango de voltaje MPPT del inversor</li>
                <li>Corriente máxima de entrada</li>
                <li>Temperatura afecta voltaje (-0.4%/gradosC típico)</li>
            </ul>''',
            key_points='''Serie: suma voltajes
Paralelo: suma corrientes
Serie-paralelo: configuración híbrida
Verificar rango MPPT del inversor
Temperatura afecta voltaje''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod3, order=max_order + 2,
            title='Cálculo de sección de cable',
            subtitle='Minimizando pérdidas eléctricas',
            content_type='text',
            duration_minutes=8,
            content='''<h2>Dimensionamiento correcto de cables</h2>
            <h3>Factores a considerar:</h3>
            <ul>
                <li><strong>Corriente máxima:</strong> Isc del panel x 1.25 (factor seguridad)</li>
                <li><strong>Distancia:</strong> De paneles a inversor</li>
                <li><strong>Caída de voltaje:</strong> Máximo 3% permitido</li>
                <li><strong>Temperatura ambiente:</strong> Derating por calor</li>
            </ul>
            <h3>Fórmula simplificada:</h3>
            <p><strong>Sección (mm2) = (2 x L x I) / (sigma x DeltaV%)</strong></p>
            <ul>
                <li>L = Longitud cable en metros</li>
                <li>I = Corriente en Amperios</li>
                <li>sigma = Conductividad (56 para cobre)</li>
                <li>DeltaV% = Caída permitida (3% del voltaje)</li>
            </ul>
            <h3>Ejemplo práctico:</h3>
            <p>String de 10 paneles, corriente 10A, distancia 20m, voltaje 400V</p>
            <p>Sección = (2 x 20 x 10) / (56 x 12) = 400/672 = 0.6 mm2</p>
            <p><strong>Usar cable solar de 4 mm2</strong> (siguiente estándar comercial)</p>
            <h3>Tipos de cable:</h3>
            <ul>
                <li><strong>DC (paneles-inversor):</strong> Cable solar certificado, doble aislamiento, UV-resistente</li>
                <li><strong>AC (inversor-tablero):</strong> Cable THHN/THW estándar</li>
                <li><strong>Tierra:</strong> Cable desnudo o verde-amarillo</li>
            </ul>''',
            key_points='''Caída de voltaje máxima: 3%
Cable solar: UV-resistente, doble aislamiento
Sección depende de corriente y distancia
Usar factor de seguridad 1.25
Conectores MC4 para DC''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod3, order=max_order + 3,
            title='Protecciones eléctricas obligatorias',
            subtitle='Seguridad del sistema',
            content_type='text',
            duration_minutes=7,
            content='''<h2>Dispositivos de protección esenciales</h2>
            <h3>Lado DC (paneles):</h3>
            <ul>
                <li><strong>Fusibles:</strong> Por cada string (1.5 x Isc)</li>
                <li><strong>Seccionador DC:</strong> Desconexión manual segura</li>
                <li><strong>Supresor de sobretensiones (SPD):</strong> Protección contra rayos Clase II</li>
                <li><strong>Diodos de bloqueo:</strong> Evitan corriente inversa (opcional con inversores modernos)</li>
            </ul>
            <h3>Lado AC (inversor-red):</h3>
            <ul>
                <li><strong>Breaker AC:</strong> Dimensionado a corriente nominal inversor</li>
                <li><strong>SPD AC:</strong> Protección contra picos de red</li>
                <li><strong>Relé de protección:</strong> Desconexión por sobrefrecuencia/subfrecuencia</li>
            </ul>
            <h3>Puesta a tierra:</h3>
            <ul>
                <li><strong>Estructura metálica:</strong> Conectada a tierra</li>
                <li><strong>Marcos de paneles:</strong> Puente equipotencial</li>
                <li><strong>Inversor:</strong> Terminal de tierra</li>
                <li><strong>Resistencia:</strong> <10 Ohm (ideal <5 Ohm)</li>
            </ul>
            <h3>Señalización:</h3>
            <ul>
                <li>Etiquetas "PELIGRO - ENERGÍA SOLAR"</li>
                <li>Diagramas en inversor y tablero</li>
                <li>Instrucciones de apagado de emergencia</li>
            </ul>''',
            key_points='''Fusibles DC por string
SPD en DC y AC (protección rayos)
Puesta a tierra < 10Ohm
Breaker AC dimensionado
Señalización obligatoria''',
            is_active=True
        )
        
        # Preguntas adicionales
        q = ModuleQuizQuestion.objects.create(
            module=mod3,
            text='En una conexión en serie de paneles, ¿qué parámetro se suma?',
            question_type='single',
            explanation='En serie se suman los voltajes, la corriente permanece constante.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='Voltaje', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Corriente', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='Potencia', is_correct=False)
        
        q = ModuleQuizQuestion.objects.create(
            module=mod3,
            text='¿Cuál es la máxima caída de voltaje permitida en cables DC?',
            question_type='single',
            explanation='Se permite máximo 3% de caída de voltaje en cables para mantener eficiencia.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='3%', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='10%', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='1%', is_correct=False)
        
        q = ModuleQuizQuestion.objects.create(
            module=mod3,
            text='Seleccione las protecciones obligatorias en lado DC (múltiple):',
            question_type='multiple',
            explanation='Fusibles, seccionador y SPD son obligatorios en el lado DC del sistema.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='Fusibles por string', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Seccionador DC', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='SPD (supresor sobretensiones)', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Medidor bidireccional', is_correct=False)

    def expand_module_4(self, mod4):
        """Expande Módulo 4: Instalación - de 3 a 6 slides, de 2 a 5 preguntas"""
        max_order = mod4.slides.aggregate(models.Max('order'))['order__max'] or 0
        
        Slide.objects.create(
            module=mod4, order=max_order + 1,
            title='Herramientas necesarias para instalación',
            subtitle='Lista completa de equipos',
            content_type='text',
            duration_minutes=6,
            content='''<h2>Equipamiento para instalación profesional</h2>
            <h3>Herramientas mecánicas:</h3>
            <ul>
                <li>Taladro percutor + brocas para concreto</li>
                <li>Destornilladores de impacto</li>
                <li>Llave dinamométrica (torque específico)</li>
                <li>Sierra de metal (corte de rieles)</li>
                <li>Nivel láser o digital</li>
                <li>Cinta métrica, flexómetro</li>
            </ul>
            <h3>Herramientas eléctricas:</h3>
            <ul>
                <li>Crimpadora MC4 (conectores solares)</li>
                <li>Pelacables calibre solar</li>
                <li>Multímetro DC (hasta 1000V)</li>
                <li>Probador de tierra</li>
                <li>Pinza amperimétrica DC</li>
            </ul>
            <h3>Seguridad:</h3>
            <ul>
                <li>Arnés anticaídas completo</li>
                <li>Línea de vida temporal</li>
                <li>Casco con barbiquejo</li>
                <li>Guantes dieléctricos</li>
                <li>Gafas de seguridad</li>
                <li>Calzado dieléctrico</li>
            </ul>''',
            key_points='''Herramientas mecánicas: taladro, destornilladores, nivel
Herramientas eléctricas: crimpadora MC4, multímetro
EPP obligatorio: arnés, casco, guantes
Multímetro DC hasta 1000V
Probador de tierra esencial''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod4, order=max_order + 2,
            title='Procedimiento de instalación paso a paso',
            subtitle='Secuencia correcta',
            content_type='text',
            duration_minutes=12,
            content='''<h2>Guía completa de instalación</h2>
            <h3>Día 1 - Preparación:</h3>
            <ol>
                <li>Inspección estructural certificada del techo</li>
                <li>Verificar orientación e inclinación</li>
                <li>Marcar ubicación de rieles y anclajes</li>
                <li>Identificar ruta de cableado</li>
                <li>Ubicar inversor (sombra, ventilación)</li>
            </ol>
            <h3>Día 2 - Estructura:</h3>
            <ol>
                <li>Perforar anclajes según marcas</li>
                <li>Impermeabilizar penetraciones (tapajuntas)</li>
                <li>Instalar rieles nivelados</li>
                <li>Verificar alineación y cuadratura</li>
                <li>Torque final en todos los tornillos</li>
            </ol>
            <h3>Día 3 - Paneles:</h3>
            <ol>
                <li>Subir paneles (mínimo 2 personas)</li>
                <li>Instalar grapas en rieles</li>
                <li>Colocar paneles verificando orientación</li>
                <li>Ajustar grapas (no exceder torque)</li>
                <li>Puentear marcos a tierra</li>
            </ol>
            <h3>Día 4 - Eléctrico:</h3>
            <ol>
                <li>Tender canalización DC</li>
                <li>Conexión de strings (serie/paralelo)</li>
                <li>String box con fusibles y SPD</li>
                <li>Conexión a inversor (verificar polaridad)</li>
                <li>Cableado AC a tablero con breaker</li>
            </ol>
            <h3>Día 5 - Comisionamiento:</h3>
            <ol>
                <li>Medición de voltaje de circuito abierto</li>
                <li>Medición de corriente de cortocircuito</li>
                <li>Verificar puesta a tierra</li>
                <li>Energizar inversor progresivamente</li>
                <li>Configurar monitoreo WiFi</li>
                <li>Pruebas de generación</li>
                <li>Entrega de documentación al cliente</li>
            </ol>''',
            key_points='''Inspección estructural previa obligatoria
Impermeabilización crucial
Verificar polaridad antes de energizar
Puesta a tierra antes de energizar
Comisionamiento progresivo''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod4, order=max_order + 3,
            title='Errores comunes y cómo evitarlos',
            subtitle='Lecciones aprendidas',
            content_type='text',
            duration_minutes=8,
            content='''<h2>Evita estos errores frecuentes</h2>
            <h3>Errores de diseño:</h3>
            <ul>
                <li>[INCORRECTO] No considerar sombras futuras (árboles creciendo)</li>
                <li>[CORRECTO] Análisis de sombra con SunEye o dron</li>
                <li>[INCORRECTO] Subestimar espacio para mantenimiento</li>
                <li>[CORRECTO] Dejar mínimo 60cm entre paneles y borde</li>
            </ul>
            <h3>Errores mecánicos:</h3>
            <ul>
                <li>[INCORRECTO] Exceso de torque en grapas (fisura marcos)</li>
                <li>[CORRECTO] Usar torquímetro: 10-15 Nm máximo</li>
                <li>[INCORRECTO] Impermeabilización incorrecta</li>
                <li>[CORRECTO] Sellante + tapajuntas + prueba de agua</li>
            </ul>
            <h3>Errores eléctricos:</h3>
            <ul>
                <li>[INCORRECTO] Invertir polaridad +/-</li>
                <li>[CORRECTO] Multímetro antes de conectar inversor</li>
                <li>[INCORRECTO] Cable subdimensionado</li>
                <li>[CORRECTO] Calcular caída de voltaje siempre</li>
                <li>[INCORRECTO] Conectores MC4 mal crimpados</li>
                <li>[CORRECTO] Usar crimpadora certificada, probar conexión</li>
            </ul>
            <h3>Errores de seguridad:</h3>
            <ul>
                <li>[INCORRECTO] Trabajar sin arnés en alturas >2m</li>
                <li>[CORRECTO] Arnés + línea de vida obligatorio</li>
                <li>[INCORRECTO] No desenergizar antes de mantenimiento</li>
                <li>[CORRECTO] Seccionador DC siempre accesible</li>
            </ul>''',
            key_points='''Análisis de sombras obligatorio
Torque correcto: 10-15 Nm
Verificar polaridad con multímetro
Impermeabilización triple (sellante + tapajuntas + prueba)
Arnés obligatorio >2m altura''',
            is_active=True
        )
        
        # Preguntas adicionales
        q = ModuleQuizQuestion.objects.create(
            module=mod4,
            text='¿Cuál es el torque máximo recomendado para grapas de paneles?',
            question_type='single',
            explanation='El torque máximo es 10-15 Nm para evitar fisuras en los marcos de aluminio.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='10-15 Nm', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='50-60 Nm', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='2-5 Nm', is_correct=False)
        
        q = ModuleQuizQuestion.objects.create(
            module=mod4,
            text='¿A qué altura es obligatorio usar arnés anticaídas?',
            question_type='single',
            explanation='En Colombia, el arnés es obligatorio para trabajos en altura superior a 1.5m, recomendado desde 2m.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='Mayor a 2 metros', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Mayor a 5 metros', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='No es necesario', is_correct=False)
        
        q = ModuleQuizQuestion.objects.create(
            module=mod4,
            text='Seleccione las verificaciones obligatorias antes de energizar (múltiple):',
            question_type='multiple',
            explanation='Antes de energizar se debe verificar polaridad, tierra y ausencia de cortocircuitos.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='Polaridad correcta (+/-)', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Puesta a tierra <10Ohm', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Voltaje de circuito abierto', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Color de los paneles', is_correct=False)

    def expand_module_5(self, mod5):
        """Expande Módulo 5: Normativa - de 3 a 6 slides, de 2 a 5 preguntas"""
        max_order = mod5.slides.aggregate(models.Max('order'))['order__max'] or 0
        
        Slide.objects.create(
            module=mod5, order=max_order + 1,
            title='Incentivos fiscales detallados',
            subtitle='Cómo aprovechar la Ley 1715',
            content_type='text',
            duration_minutes=10,
            content='''<h2>Beneficios tributarios paso a paso</h2>
            <h3>1. Exención de IVA (19%):</h3>
            <ul>
                <li><strong>Aplica a:</strong> Paneles, inversores, estructuras, baterías</li>
                <li><strong>Requisito:</strong> Proyecto registrado en UPME</li>
                <li><strong>Ahorro:</strong> ~$3 millones en sistema de $16M</li>
            </ul>
            <h3>2. Deducción del 50% en renta:</h3>
            <ul>
                <li><strong>Beneficio:</strong> Deducir 50% inversión del impuesto de renta</li>
                <li><strong>Plazo:</strong> 5 años (10% anual)</li>
                <li><strong>Ejemplo:</strong> Inversión $16M = $8M deducibles</li>
                <li><strong>Límite:</strong> Máximo 50% de la renta líquida del año</li>
            </ul>
            <h3>3. Depreciación acelerada:</h3>
            <ul>
                <li><strong>Beneficio:</strong> Amortizar en 3-5 años vs 10 años normal</li>
                <li><strong>Ventaja fiscal:</strong> Menor base gravable inicialmente</li>
            </ul>
            <h3>4. Exención aranceles:</h3>
            <ul>
                <li><strong>Aplica:</strong> Importación de equipos certificados</li>
                <li><strong>Ahorro:</strong> 5-15% del valor CIF</li>
            </ul>
            <h3>Proceso de aplicación:</h3>
            <ol>
                <li>Obtener certificación RETIE del proyecto</li>
                <li>Registrar en UPME (Resolución 203 de 2020)</li>
                <li>Solicitar aval ANLA (si aplica)</li>
                <li>Declarar beneficios en renta anual</li>
            </ol>''',
            key_points='''Exención IVA: ~19% ahorro
Deducción renta: 50% en 5 años
Depreciación acelerada: 3-5 años
Registro UPME obligatorio
Beneficios acumulables''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod5, order=max_order + 2,
            title='Medición neta y compensación',
            subtitle='Resolución CREG 030/2018',
            content_type='text',
            duration_minutes=9,
            content='''<h2>Cómo funciona la medición neta en Colombia</h2>
            <h3>Principio básico:</h3>
            <p>La energía que generas y no consumes se "inyecta" a la red eléctrica, acumulando créditos 
            que pueden usarse cuando consumes más de lo que generas (noches, días nublados).</p>
            <h3>Características CREG 030/2018:</h3>
            <ul>
                <li><strong>Tamaño:</strong> Hasta 1 MW (autogeneración pequeña escala)</li>
                <li><strong>Medidor:</strong> Bidireccional (registra consumo e inyección)</li>
                <li><strong>Créditos:</strong> Válidos por 12 meses calendario</li>
                <li><strong>Valorización:</strong> Al costo del kWh de tu tarifa</li>
            </ul>
            <h3>Ejemplo mes típico:</h3>
            <ul>
                <li>Generación solar: 600 kWh</li>
                <li>Consumo total: 500 kWh</li>
                <li>Autoconsumo directo: 300 kWh (mientras generabas)</li>
                <li>Inyectado a red: 300 kWh (excedente)</li>
                <li>Consumido de red: 200 kWh (noche)</li>
                <li><strong>Balance neto: +100 kWh crédito</strong></li>
                <li>Factura: Cargo fijo + (200 - 300) = Solo cargo fijo</li>
            </ul>
            <h3>Consideraciones:</h3>
            <ul>
                <li>Cargo fijo siempre se paga</li>
                <li>Créditos no generan pago monetario, solo compensan consumo</li>
                <li>Después de 12 meses, créditos no usados se pierden</li>
                <li>Ideal: dimensionar para autoconsumo, no sobreproducir</li>
            </ul>''',
            key_points='''Medición neta: inyección compensa consumo
Créditos válidos 12 meses
Tarifa: mismo valor kWh
Sistema ideal: 80-100% autoconsumo
Cargo fijo siempre se cobra''',
            is_active=True
        )
        
        Slide.objects.create(
            module=mod5, order=max_order + 3,
            title='Financiamiento de proyectos solares',
            subtitle='Opciones de pago',
            content_type='text',
            duration_minutes=8,
            content='''<h2>¿Cómo pagar tu sistema solar?</h2>
            <h3>1. Pago de contado:</h3>
            <ul>
                <li><strong>Descuento:</strong> 5-10% típicamente</li>
                <li><strong>ROI:</strong> Más rápido (4-5 años)</li>
                <li><strong>Riesgo:</strong> Desembolso inicial alto</li>
            </ul>
            <h3>2. Crédito bancario verde:</h3>
            <ul>
                <li><strong>Bancos:</strong> Bancolombia, Davivienda, Banco Agrario</li>
                <li><strong>Tasa:</strong> 12-18% EA</li>
                <li><strong>Plazo:</strong> 5-10 años</li>
                <li><strong>Cuota:</strong> Puede ser menor que ahorro eléctrico</li>
                <li><strong>Requisitos:</strong> Estudio crédito, garantías</li>
            </ul>
            <h3>3. Leasing:</h3>
            <ul>
                <li>Equipo en arriendo con opción de compra</li>
                <li>Ventaja fiscal: Deducible como gasto</li>
                <li>No requiere gran desembolso inicial</li>
            </ul>
            <h3>4. PPA (Power Purchase Agreement):</h3>
            <ul>
                <li>Tercero instala sistema sin costo inicial</li>
                <li>Pagas por kWh generado (menor a tarifa red)</li>
                <li>Mantenimiento incluido</li>
                <li>Plazo: 10-20 años</li>
                <li>Al final: opción de compra o renovación</li>
            </ul>
            <h3>Comparativa ejemplo ($16M, ahorro $3.45M/año):</h3>
            <ul>
                <li><strong>Contado:</strong> ROI 4.6 años</li>
                <li><strong>Crédito 15% a 7 años:</strong> Cuota $300k/mes, ROI 7 años</li>
                <li><strong>PPA:</strong> Ahorro inmediato 15-25% factura, sin inversión</li>
            </ul>''',
            key_points='''Contado: ROI más rápido
Crédito verde: 12-18% EA, 5-10 años
PPA: sin inversión inicial
Cuota puede < ahorro eléctrico
Incentivos fiscales mejoran ROI''',
            is_active=True
        )
        
        # Preguntas adicionales
        q = ModuleQuizQuestion.objects.create(
            module=mod5,
            text='¿Qué porcentaje de la inversión se puede deducir de renta con Ley 1715?',
            question_type='single',
            explanation='La Ley 1715 permite deducir el 50% de la inversión en energías renovables del impuesto de renta.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='50%', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='100%', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='25%', is_correct=False)
        
        q = ModuleQuizQuestion.objects.create(
            module=mod5,
            text='¿Por cuánto tiempo son válidos los créditos de energía en medición neta?',
            question_type='single',
            explanation='Los créditos de energía inyectada son válidos por 12 meses calendario.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='12 meses', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='24 meses', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='6 meses', is_correct=False)
        
        q = ModuleQuizQuestion.objects.create(
            module=mod5,
            text='Seleccione los beneficios tributarios de Ley 1715 (múltiple):',
            question_type='multiple',
            explanation='Ley 1715 incluye exención de IVA, deducción de renta y exención de aranceles.',
            is_active=True
        )
        ModuleQuizOption.objects.create(question=q, text='Exención de IVA', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Deducción 50% renta', is_correct=True)
        ModuleQuizOption.objects.create(question=q, text='Subsidio directo 100%', is_correct=False)
        ModuleQuizOption.objects.create(question=q, text='Exención de aranceles', is_correct=True)
