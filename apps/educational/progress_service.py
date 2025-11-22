from apps.educational.course_models import CourseEnrollment, Course

class ProgressService:
    """Servicio para cálculo y actualización de progreso del curso."""

    def recompute_enrollment(self, enrollment: CourseEnrollment):
        course = enrollment.course
        user = enrollment.user
        active_modules = course.modules.filter(is_active=True).count()
        passed_modules = course.modules.filter(is_active=True, attempts__user=user, attempts__passed=True).distinct().count()
        progress = (passed_modules / active_modules * 100) if active_modules else 0
        enrollment.progress_percent = round(progress, 2)
        enrollment.all_modules_passed = passed_modules == active_modules and active_modules > 0
        enrollment.final_exam_unlocked = enrollment.all_modules_passed
        enrollment.save(update_fields=['progress_percent', 'all_modules_passed', 'final_exam_unlocked'])
        return enrollment
