from celery import shared_task


@shared_task
def update_ley_1715_task():
    """Tarea Celery para actualizar la Ley 1715 desde la fuente oficial."""
    from .services import update_ley_1715_data
    update_ley_1715_data()


@shared_task
def update_ley_2099_task():
    """Tarea Celery para actualizar la Ley 2099 desde la fuente oficial."""
    from .services import update_ley_2099_data
    update_ley_2099_data()
