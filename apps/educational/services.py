from django.db import transaction
from typing import Dict, List
import uuid

from apps.educational.course_models import (
    ModuleAttempt, ModuleAnswer, CourseEnrollment,
    FinalExamAttempt, CourseCertificate, Course
)
from .progress_service import ProgressService


class QuizEvaluationService:
    """Servicio para evaluar cuestionarios de módulos y actualizar progreso."""

    def evaluate_attempt(self, attempt: ModuleAttempt, answers_payload: Dict[int, List[int]]):
        if attempt.state not in ('in_progress', 'submitted'):
            raise ValueError('El intento no está en estado válido para evaluación.')

        module = attempt.module
        questions = module.questions.filter(is_active=True)
        total = questions.count()
        if total == 0:
            attempt.mark_submitted(score=100, passed=True)
            return {'score': 100, 'passed': True, 'details': []}

        details = []
        with transaction.atomic():
            for question in questions:
                selected_ids = answers_payload.get(question.id, [])
                answer = ModuleAnswer.objects.create(attempt=attempt, question=question)
                valid_options = list(question.options.filter(id__in=selected_ids, is_active=True))
                answer.selected_options.set(valid_options)
                answer.evaluate()
                details.append({
                    'question_id': question.id,
                    'is_correct': answer.is_correct,
                    'selected': selected_ids,
                })

            correct = attempt.answers.filter(is_correct=True).count()
            score = int((correct / total) * 100)
            passed = score >= module.required_pass_score
            attempt.mark_submitted(score=score, passed=passed)

            # Actualizar progreso del enrollment si existe
            try:
                enrollment = CourseEnrollment.objects.get(user=attempt.user, course=module.course)
            except CourseEnrollment.DoesNotExist:
                enrollment = None
            if enrollment:
                ProgressService().recompute_enrollment(enrollment)

        return {'score': score, 'passed': passed, 'details': details}


class FinalExamService:
    """Servicio para manejar intentos del examen final y certificación."""

    def evaluate_final_exam(self, attempt: FinalExamAttempt, answers_payload: Dict[int, List[int]]):
        if attempt.state not in ('in_progress', 'submitted'):
            raise ValueError('El intento no está en estado válido para evaluación.')

        course = attempt.course
        questions = course.final_questions.filter(is_active=True)
        # Validar límite de intentos si aplica
        if course.max_final_attempts and attempt.attempt_number > course.max_final_attempts:
            raise ValueError('Se alcanzó el número máximo de intentos del examen final.')
        total = questions.count()
        if total == 0:
            attempt.mark_submitted(score=100, passed=True)
            return {'score': 100, 'passed': True, 'details': []}

        details = []
        with transaction.atomic():
            correct_count = 0
            for question in questions:
                selected_ids = set(answers_payload.get(question.id, []))
                correct_ids = set(question.correct_options().values_list('id', flat=True))
                if question.question_type == 'single':
                    is_correct = len(selected_ids) == 1 and selected_ids == correct_ids
                else:
                    is_correct = selected_ids == correct_ids and len(selected_ids) > 0
                if is_correct:
                    correct_count += 1
                details.append({
                    'question_id': question.id,
                    'is_correct': is_correct,
                    'selected': list(selected_ids),
                })

            score = int((correct_count / total) * 100)
            passed = score >= course.final_pass_score
            attempt.mark_submitted(score=score, passed=passed)

            certificate = None
            if passed:
                certificate = self._issue_certificate(attempt.user, course, score)

        return {
            'score': score, 
            'passed': passed, 
            'correct': correct_count,
            'total': total,
            'required': course.final_pass_score,
            'course_slug': course.slug,
            'details': details, 
            'certificate_code': certificate.certificate_code if passed else None
        }

    def _issue_certificate(self, user, course: Course, score: int):
        from .certificate_service import CertificatePDFService
        
        existing = CourseCertificate.objects.filter(user=user, course=course).first()
        if existing:
            # Generar PDF si no existe
            if not existing.pdf_file:
                CertificatePDFService().generate_pdf(existing, regenerate=False)
            return existing  # Evitar duplicados
        
        code = f"CUR-{course.pk}-{user.pk}-{uuid.uuid4().hex[:8]}".upper()
        certificate = CourseCertificate.objects.create(
            user=user,
            course=course,
            certificate_code=code,
            final_score=score,
            metadata={'course_title': course.title, 'user_email': user.email}
        )
        
        # Generar PDF automáticamente
        CertificatePDFService().generate_pdf(certificate, regenerate=False)
        
        return certificate
