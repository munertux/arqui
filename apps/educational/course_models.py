from django.db import models
from django.utils import timezone
from django.conf import settings

from apps.core.models import BaseModel
from apps.accounts.models import User

# Niveles sugeridos del curso
COURSE_LEVELS = [
    ('basic', 'Básico'),
    ('intermediate', 'Intermedio'),
    ('advanced', 'Avanzado'),
]

PUBLISH_STATES = [
    ('draft', 'Borrador'),
    ('published', 'Publicado'),
    ('archived', 'Archivado'),
]

ATTEMPT_STATES = [
    ('in_progress', 'En progreso'),
    ('submitted', 'Enviado'),
    ('passed', 'Aprobado'),
    ('failed', 'Fallido'),
]

QUESTION_TYPES = [
    ('single', 'Selección única'),
    ('multiple', 'Selección múltiple'),
]

class Course(BaseModel):
    """Curso teórico de energía solar compuesto por módulos"""
    title = models.CharField(max_length=200, verbose_name='Título')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Descripción')
    level = models.CharField(max_length=15, choices=COURSE_LEVELS, default='basic', verbose_name='Nivel')
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, verbose_name='Horas estimadas')
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='courses', verbose_name='Autor')
    category = models.ForeignKey('educational.Category', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Categoría')
    final_pass_score = models.PositiveIntegerField(default=70, verbose_name='Puntaje aprobación examen final', help_text='Porcentaje mínimo para aprobar examen final')
    publish_state = models.CharField(max_length=10, choices=PUBLISH_STATES, default='draft', verbose_name='Estado de publicación')
    max_final_attempts = models.PositiveIntegerField(default=0, verbose_name='Máx intentos examen final', help_text='0 = ilimitado')

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def modules_count(self):
        return self.modules.filter(is_active=True).count()

    def active_modules(self):
        return self.modules.filter(is_active=True).order_by('order')

class Module(BaseModel):
    """Módulo de un curso"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules', verbose_name='Curso')
    title = models.CharField(max_length=200, verbose_name='Título')
    order = models.PositiveIntegerField(verbose_name='Orden')
    summary = models.TextField(blank=True, verbose_name='Resumen')
    required_pass_score = models.PositiveIntegerField(default=70, verbose_name='Puntaje mínimo', help_text='Porcentaje mínimo para aprobar el cuestionario del módulo')

    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['course', 'order']
        unique_together = ('course', 'order')

    def __str__(self):
        return f"{self.course.title} - {self.title}" 

    @property
    def slides_count(self):
        return self.slides.filter(is_active=True).count()

CONTENT_TYPES = [
    ('text', 'Texto'),
    ('video', 'Video'),
    ('image', 'Imagen'),
    ('quiz', 'Quiz interactivo'),
]

class Slide(BaseModel):
    """Diapositiva (contenido secuencial dentro de un módulo)"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='slides', verbose_name='Módulo')
    order = models.PositiveIntegerField(verbose_name='Orden')
    title = models.CharField(max_length=200, verbose_name='Título')
    subtitle = models.CharField(max_length=300, blank=True, verbose_name='Subtítulo')
    content = models.TextField(verbose_name='Contenido', help_text='HTML o Markdown del cuerpo de la diapositiva')
    
    # Contenido multimedia estructurado
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='text', verbose_name='Tipo de contenido')
    video_url = models.URLField(blank=True, verbose_name='URL de video', help_text='YouTube, Vimeo, etc.')
    image = models.ImageField(upload_to='educational/slides/', blank=True, null=True, verbose_name='Imagen')
    
    # Metadata para mejor presentación
    duration_minutes = models.PositiveIntegerField(default=5, verbose_name='Duración estimada (min)')
    key_points = models.TextField(blank=True, verbose_name='Puntos clave', help_text='Puntos principales separados por líneas')
    additional_resources = models.TextField(blank=True, verbose_name='Recursos adicionales', help_text='Enlaces o referencias adicionales')

    class Meta:
        verbose_name = 'Diapositiva'
        verbose_name_plural = 'Diapositivas'
        ordering = ['module', 'order']
        unique_together = ('module', 'order')

    def __str__(self):
        return f"Slide {self.order} - {self.module.title}"
    
    def get_key_points_list(self):
        """Retorna los puntos clave como lista"""
        if self.key_points:
            return [p.strip() for p in self.key_points.split('\n') if p.strip()]
        return [] 

class ModuleQuizQuestion(BaseModel):
    """Pregunta del cuestionario de un módulo"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='questions', verbose_name='Módulo')
    text = models.TextField(verbose_name='Texto de la pregunta')
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='single', verbose_name='Tipo de pregunta')
    explanation = models.TextField(blank=True, verbose_name='Explicación', help_text='Retroalimentación mostrada tras responder')

    class Meta:
        verbose_name = 'Pregunta de módulo'
        verbose_name_plural = 'Preguntas de módulo'
        ordering = ['module', 'created_at']

    def __str__(self):
        return f"Pregunta {self.pk} - {self.module.title}" 

    def correct_options(self):
        return self.options.filter(is_correct=True)

class ModuleQuizOption(BaseModel):
    """Opción de respuesta de una pregunta"""
    question = models.ForeignKey(ModuleQuizQuestion, on_delete=models.CASCADE, related_name='options', verbose_name='Pregunta')
    text = models.CharField(max_length=300, verbose_name='Texto')
    is_correct = models.BooleanField(default=False, verbose_name='Correcta')

    class Meta:
        verbose_name = 'Opción de pregunta'
        verbose_name_plural = 'Opciones de pregunta'
        ordering = ['question', 'created_at']

    def __str__(self):
        return f"Opción {self.pk} - Pregunta {self.question.pk}" 

class CourseEnrollment(BaseModel):
    """Inscripción de un usuario a un curso"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_enrollments', verbose_name='Usuario')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name='Curso')
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Progreso (%)')
    all_modules_passed = models.BooleanField(default=False, verbose_name='Todos los módulos aprobados')
    final_exam_unlocked = models.BooleanField(default=False, verbose_name='Examen final desbloqueado')

    class Meta:
        verbose_name = 'Inscripción de curso'
        verbose_name_plural = 'Inscripciones de curso'
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} en {self.course.title}" 

class ModuleAttempt(BaseModel):
    """Intento de cuestionario de un módulo"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_attempts', verbose_name='Usuario')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='attempts', verbose_name='Módulo')
    started_at = models.DateTimeField(default=timezone.now, verbose_name='Inicio')
    finished_at = models.DateTimeField(blank=True, null=True, verbose_name='Fin')
    score = models.PositiveIntegerField(default=0, verbose_name='Puntaje (%)')
    passed = models.BooleanField(default=False, verbose_name='Aprobado')
    state = models.CharField(max_length=15, choices=ATTEMPT_STATES, default='in_progress', verbose_name='Estado')
    attempt_number = models.PositiveIntegerField(default=1, verbose_name='Número de intento')
    current_slide = models.PositiveIntegerField(default=1, verbose_name='Diapositiva actual')

    class Meta:
        verbose_name = 'Intento de módulo'
        verbose_name_plural = 'Intentos de módulo'
        ordering = ['-started_at']
        unique_together = ('user', 'module', 'attempt_number')

    def __str__(self):
        return f"Intento {self.attempt_number} - {self.user.email} - {self.module.title}" 

    def mark_submitted(self, score, passed):
        self.score = score
        self.passed = passed
        self.state = 'passed' if passed else 'failed'
        self.finished_at = timezone.now()
        self.save(update_fields=['score', 'passed', 'state', 'finished_at'])

class ModuleAnswer(BaseModel):
    """Respuesta del usuario a una pregunta en un intento"""
    attempt = models.ForeignKey(ModuleAttempt, on_delete=models.CASCADE, related_name='answers', verbose_name='Intento')
    question = models.ForeignKey(ModuleQuizQuestion, on_delete=models.CASCADE, related_name='answers', verbose_name='Pregunta')
    selected_options = models.ManyToManyField(ModuleQuizOption, related_name='answers', verbose_name='Opciones seleccionadas')
    is_correct = models.BooleanField(default=False, verbose_name='Correcta')

    class Meta:
        verbose_name = 'Respuesta de módulo'
        verbose_name_plural = 'Respuestas de módulo'
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f"Resp {self.pk} - Intento {self.attempt.pk}" 

    def evaluate(self):
        correct_ids = set(self.question.correct_options().values_list('id', flat=True))
        selected_ids = set(self.selected_options.values_list('id', flat=True))
        if self.question.question_type == 'single':
            self.is_correct = len(selected_ids) == 1 and selected_ids == correct_ids
        else:  # multiple
            self.is_correct = selected_ids == correct_ids and len(selected_ids) > 0
        self.save(update_fields=['is_correct'])


class FinalExamQuestion(BaseModel):
    """Pregunta del examen final del curso"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='final_questions', verbose_name='Curso')
    text = models.TextField(verbose_name='Texto de la pregunta')
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='single', verbose_name='Tipo de pregunta')
    explanation = models.TextField(blank=True, verbose_name='Explicación')

    class Meta:
        verbose_name = 'Pregunta examen final'
        verbose_name_plural = 'Preguntas examen final'
        ordering = ['course', 'created_at']

    def __str__(self):
        return f"Final Q {self.pk} - {self.course.title}"

    def correct_options(self):
        return self.final_options.filter(is_correct=True)


class FinalExamOption(BaseModel):
    """Opción de una pregunta del examen final"""
    question = models.ForeignKey(FinalExamQuestion, on_delete=models.CASCADE, related_name='final_options', verbose_name='Pregunta')
    text = models.CharField(max_length=300, verbose_name='Texto')
    is_correct = models.BooleanField(default=False, verbose_name='Correcta')

    class Meta:
        verbose_name = 'Opción examen final'
        verbose_name_plural = 'Opciones examen final'
        ordering = ['question', 'created_at']

    def __str__(self):
        return f"Final Opt {self.pk} - Q {self.question.pk}"


class FinalExamAttempt(BaseModel):
    """Intento del examen final"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='final_exam_attempts', verbose_name='Usuario')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='final_attempts', verbose_name='Curso')
    started_at = models.DateTimeField(default=timezone.now, verbose_name='Inicio')
    finished_at = models.DateTimeField(blank=True, null=True, verbose_name='Fin')
    score = models.PositiveIntegerField(default=0, verbose_name='Puntaje (%)')
    passed = models.BooleanField(default=False, verbose_name='Aprobado')
    state = models.CharField(max_length=15, choices=ATTEMPT_STATES, default='in_progress', verbose_name='Estado')
    attempt_number = models.PositiveIntegerField(default=1, verbose_name='Número de intento')

    class Meta:
        verbose_name = 'Intento examen final'
        verbose_name_plural = 'Intentos examen final'
        ordering = ['-started_at']
        unique_together = ('user', 'course', 'attempt_number')

    def __str__(self):
        return f"Exam Attempt {self.attempt_number} - {self.user.email} - {self.course.title}"

    def mark_submitted(self, score, passed):
        self.score = score
        self.passed = passed
        self.state = 'passed' if passed else 'failed'
        self.finished_at = timezone.now()
        self.save(update_fields=['score', 'passed', 'state', 'finished_at'])


class FinalExamAnswer(BaseModel):
    """Respuesta del usuario a una pregunta del examen final"""
    attempt = models.ForeignKey(FinalExamAttempt, on_delete=models.CASCADE, related_name='answers', verbose_name='Intento')
    question = models.ForeignKey(FinalExamQuestion, on_delete=models.CASCADE, related_name='answers', verbose_name='Pregunta')
    selected_options = models.ManyToManyField(FinalExamOption, related_name='answers', verbose_name='Opciones seleccionadas')
    is_correct = models.BooleanField(default=False, verbose_name='Correcta')
    time_spent_seconds = models.PositiveIntegerField(default=0, verbose_name='Tiempo dedicado (seg)')

    class Meta:
        verbose_name = 'Respuesta examen final'
        verbose_name_plural = 'Respuestas examen final'
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f"Resp examen {self.pk} - Intento {self.attempt.pk}"


class SlideView(BaseModel):
    """Registro de visualización de diapositivas por usuario"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='slide_views', verbose_name='Usuario')
    slide = models.ForeignKey(Slide, on_delete=models.CASCADE, related_name='views', verbose_name='Diapositiva')
    enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE, related_name='slide_views', verbose_name='Inscripción')
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name='Vista el')
    time_spent_seconds = models.PositiveIntegerField(default=0, verbose_name='Tiempo dedicado (seg)')
    completed = models.BooleanField(default=False, verbose_name='Completada')

    class Meta:
        verbose_name = 'Vista de diapositiva'
        verbose_name_plural = 'Vistas de diapositivas'
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user.email} - {self.slide.title}"


class UserProgress(BaseModel):
    """Progreso granular del usuario en el curso (resumen consolidado)"""
    enrollment = models.OneToOneField(CourseEnrollment, on_delete=models.CASCADE, related_name='detailed_progress', verbose_name='Inscripción')
    total_slides_viewed = models.PositiveIntegerField(default=0, verbose_name='Diapositivas vistas')
    total_time_minutes = models.PositiveIntegerField(default=0, verbose_name='Tiempo total (min)')
    modules_passed_count = models.PositiveIntegerField(default=0, verbose_name='Módulos aprobados')
    quiz_attempts_count = models.PositiveIntegerField(default=0, verbose_name='Intentos de quiz')
    exam_attempts_count = models.PositiveIntegerField(default=0, verbose_name='Intentos de examen')
    best_exam_score = models.PositiveIntegerField(default=0, verbose_name='Mejor puntaje examen')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Última actividad')

    class Meta:
        verbose_name = 'Progreso de usuario'
        verbose_name_plural = 'Progresos de usuario'

    def __str__(self):
        return f"Progreso {self.enrollment.user.email} - {self.enrollment.course.title}"


class CourseCertificate(BaseModel):
    """Certificado emitido al aprobar curso"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_certificates', verbose_name='Usuario')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates', verbose_name='Curso')
    issued_at = models.DateTimeField(default=timezone.now, verbose_name='Emitido')
    certificate_code = models.CharField(max_length=60, unique=True, verbose_name='Código certificado')
    final_score = models.PositiveIntegerField(default=0, verbose_name='Puntaje final')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Metadatos')
    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True, verbose_name='Archivo PDF')
    is_revoked = models.BooleanField(default=False, verbose_name='Revocado')

    class Meta:
        verbose_name = 'Certificado de curso'
        verbose_name_plural = 'Certificados de curso'
        ordering = ['-issued_at']
        unique_together = ('user', 'course')

    def __str__(self):
        return f"Certificado {self.certificate_code} - {self.course.title}"

    @property
    def is_valid(self):
        return not self.is_revoked
