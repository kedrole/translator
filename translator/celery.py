import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'translator.settings')

app = Celery('translator')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {

    'STAGE_parse_articles_with_stage_parsing': {
        "task": "main.processing_stages.STAGE_parse_articles_with_stage_parsing",
        "schedule": 40
    },

}

'''
    'STAGE_add_artices_from_articlelistpages_to_parsing_queue': {
        "task": "main.processing_stages.STAGE_add_artices_from_articlelistpages_to_parsing_queue",
        "schedule": 30
    },


    'STAGE_get_uniquedata_articles_with_stage_ChekingOriginalUnique_and_autoreject_if_needed': {
        "task": "main.processing_stages.STAGE_get_uniquedata_articles_with_stage_ChekingOriginalUnique_and_autoreject_if_needed",
        "schedule": 20
    },

    'STAGE_get_uniquedata_articles_with_stage_CheckingTranslationUnique_and_autoreject_if_needed': {
        "task": "main.processing_stages.STAGE_get_uniquedata_articles_with_stage_CheckingTranslationUnique_and_autoreject_if_needed",
        "schedule": 20
    },

    'STAGE_get_translation_articles_with_stage_autotranslating': {
        "task": "main.processing_stages.STAGE_get_translation_articles_with_stage_autotranslating",
        "schedule": 20
    },
    '''