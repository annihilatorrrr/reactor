from django.urls import path
from django.conf import settings

from .views import process_update_view

app_name = 'bot'
urlpatterns = [
    path(f'webhook/{settings.TG_BOT_TOKEN}', process_update_view, name='webhook'),
]
