# chat/apps.py
from django.apps import AppConfig

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    def ready(self):
        # Prevent double execution during auto-reload
        import os
        if os.environ.get('RUN_MAIN') == 'true':
            from .rag_service import ingest_document, sample_news_articles
            for doc in sample_news_articles:
                ingest_document(doc["doc_id"], doc["text"])