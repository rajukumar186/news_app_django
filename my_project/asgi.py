# my_project/asgi.py
import os
from django.core.asgi import get_asgi_application

# 1. MUST BE FIRST: Set the default Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings') # Replace 'my_project.settings' with your actual settings module path if different

# 2. Initialize Django ASGI application BEFORE importing routing or consumers
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})