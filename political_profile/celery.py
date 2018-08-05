from celery import Celery
from django.conf import settings

celery = Celery('political_profile', broker=settings.BROKER_URL)

celery.config_from_object('django.conf:settings')
celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
