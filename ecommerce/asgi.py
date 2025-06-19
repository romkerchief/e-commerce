"""
ASGI config for ecommerce project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings') 
import django 
django.setup() 
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler 
from channels.routing import ProtocolTypeRouter, URLRouter #type:ignore
from channels.auth import AuthMiddlewareStack #type:ignore
import chat.routing 


# Get the standard Django ASGI application first.
django_asgi_app = get_asgi_application()

# Wrap the Django app with ASGIStaticFilesHandler for development static file serving
http_application = ASGIStaticFilesHandler(django_asgi_app)

application = ProtocolTypeRouter({
    # "http": django_asgi_app, # Old way
    "http": http_application,  # Use the wrapped app for HTTP requests
    "websocket": AuthMiddlewareStack( # AuthMiddlewareStack adds user to scope
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
