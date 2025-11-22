from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.educational.models import Category
from apps.educational.course_models import (
    Course, Module, Slide,
    ModuleQuizQuestion, ModuleQuizOption,
    CourseEnrollment, ModuleAttempt, ModuleAnswer,
    FinalExamQuestion, FinalExamOption, FinalExamAttempt, CourseCertificate
)
from apps.educational.certificate_service import CertificatePDFService

User = get_user_model()

class Command(BaseCommand):
    help = "Crea datos de ejemplo para probar el flujo completo de cursos (curso, módulos, slides, quiz, examen final, certificado)."

    def handle(self, *args, **options):
        # Usuarios
        author, _ = User.objects.get_or_create(email='editor_demo@example.com', defaults={
            'username': 'editor_demo', 'password': 'pass', 'role': 'editor'
        })
        student, _ = User.objects.get_or_create(email='student_demo@example.com', defaults={
            'username': 'student_demo', 'password': 'pass', 'role': 'client'
        })

        # Categoría
        category, _ = Category.objects.get_or_create(name='Demo Solar', slug='demo-solar')

        # Curso
        course, created_course = Course.objects.get_or_create(
            slug='curso-demo-solar',
            defaults={
                'title': 'Curso Demo Solar',
                'description': 'Curso de demostración para validar el flujo educativo.',
                'level': 'basic',
                'author': author,
                'category': category,
                'publish_state': 'published'
            }
        )

        # Módulos
        module1, _ = Module.objects.get_or_create(course=course, order=1, defaults={'title': 'Fundamentos', 'summary': 'Base teórica'})
        module2, _ = Module.objects.get_or_create(course=course, order=2, defaults={'title': 'Instalación', 'summary': 'Instalación básica'})

        # Slides módulo 1
        if module1.slides.count() == 0:
            for i in range(1, 4):
                Slide.objects.create(module=module1, order=i, title=f'Slide {i}', content=f'Contenido {i}')

        # Quiz preguntas módulo1
        if module1.questions.count() == 0:
            q1 = ModuleQuizQuestion.objects.create(module=module1, text='¿Qué es un panel solar?', question_type='single')
            ModuleQuizOption.objects.create(question=q1, text='Dispositivo que convierte luz en electricidad', is_correct=True)
            ModuleQuizOption.objects.create(question=q1, text='Batería que almacena luz', is_correct=False)
            q2 = ModuleQuizQuestion.objects.create(module=module1, text='Seleccione componentes', question_type='multiple')
            ModuleQuizOption.objects.create(question=q2, text='Celdas fotovoltaicas', is_correct=True)
            ModuleQuizOption.objects.create(question=q2, text='Marco', is_correct=True)
            ModuleQuizOption.objects.create(question=q2, text='Agua', is_correct=False)

        # Examen final preguntas
        if course.final_questions.count() == 0:
            fq1 = FinalExamQuestion.objects.create(course=course, text='El panel solar convierte...', question_type='single')
            FinalExamOption.objects.create(question=fq1, text='Luz en electricidad', is_correct=True)
            FinalExamOption.objects.create(question=fq1, text='Electricidad en calor', is_correct=False)
            fq2 = FinalExamQuestion.objects.create(course=course, text='Componentes clave', question_type='multiple')
            FinalExamOption.objects.create(question=fq2, text='Celdas fotovoltaicas', is_correct=True)
            FinalExamOption.objects.create(question=fq2, text='Marco', is_correct=True)
            FinalExamOption.objects.create(question=fq2, text='Agua', is_correct=False)

        # Inscripción
        enrollment, _ = CourseEnrollment.objects.get_or_create(user=student, course=course)

        # Aprobar módulo 1
        if not ModuleAttempt.objects.filter(user=student, module=module1, passed=True).exists():
            attempt1 = ModuleAttempt.objects.create(user=student, module=module1, attempt_number=1, current_slide=module1.slides_count)
            for question in module1.questions.all():
                ans = ModuleAnswer.objects.create(attempt=attempt1, question=question)
                ans.selected_options.set(question.correct_options())
                ans.evaluate()
            total = module1.questions.count()
            correct = attempt1.answers.filter(is_correct=True).count()
            score = int((correct / total) * 100)
            attempt1.mark_submitted(score=score, passed=True)

        # Aprobar módulo 2 (sin preguntas)
        if not ModuleAttempt.objects.filter(user=student, module=module2, passed=True).exists():
            attempt2 = ModuleAttempt.objects.create(user=student, module=module2, attempt_number=1, current_slide=module2.slides_count)
            attempt2.mark_submitted(score=100, passed=True)

        # Actualizar progreso manual (simple)
        passed_modules = course.modules.filter(attempts__user=student, attempts__passed=True).distinct().count()
        active_modules = course.modules.count()
        progress = (passed_modules / active_modules) * 100 if active_modules else 0
        enrollment.progress_percent = progress
        enrollment.all_modules_passed = passed_modules == active_modules
        enrollment.final_exam_unlocked = enrollment.all_modules_passed
        enrollment.save()

        # Examen final
        if not FinalExamAttempt.objects.filter(user=student, course=course, passed=True).exists():
            exam_attempt = FinalExamAttempt.objects.create(user=student, course=course, attempt_number=1)
            correct_count = 0
            final_questions = course.final_questions.all()
            for q in final_questions:
                selected_ids = set(q.correct_options().values_list('id', flat=True))
                correct_ids = set(selected_ids)
                if q.question_type == 'single':
                    is_correct = len(selected_ids) == 1 and selected_ids == correct_ids
                else:
                    is_correct = selected_ids == correct_ids and len(selected_ids) > 0
                if is_correct:
                    correct_count += 1
            final_score = int((correct_count / final_questions.count()) * 100) if final_questions.exists() else 100
            exam_attempt.mark_submitted(score=final_score, passed=True)

        # Certificado
        certificate, created_cert = CourseCertificate.objects.get_or_create(
            user=student,
            course=course,
            defaults={
                'certificate_code': 'CUR-DEMO',
                'final_score': FinalExamAttempt.objects.filter(user=student, course=course, passed=True).order_by('-created_at').first().score if FinalExamAttempt.objects.filter(user=student, course=course, passed=True).exists() else 100,
                'metadata': {'seed': True}
            }
        )

        # Generar PDF si no existe
        if not certificate.pdf_file:
            CertificatePDFService().generate_pdf(certificate, regenerate=True)

        self.stdout.write(self.style.SUCCESS('Curso de demostración listo.'))
        self.stdout.write(f"Autor: {author.email} | Student: {student.email}")
        self.stdout.write(f"URL curso (admin): /admin/educational/course/{course.id}/change/")
        self.stdout.write(f"Certificado: {certificate.certificate_code} | PDF: {'OK' if certificate.pdf_file else 'NO'}")
