import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siese.settings')

app = Celery('siese')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Programación: actualizar Ley 1715 todos los días a medianoche
app.conf.beat_schedule = {
    'update-ley-1715-midnight': {
        'task': 'apps.regulatory.tasks.update_ley_1715_task',
        'schedule': crontab(minute=0, hour=0),
    },
    'update-ley-2099-midnight': {
        'task': 'apps.regulatory.tasks.update_ley_2099_task',
        'schedule': crontab(minute=0, hour=0),
    },
}
