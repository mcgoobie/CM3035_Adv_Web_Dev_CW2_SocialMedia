# ASGI Application - for websocket/chatroom
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
import chat.routing

application = ProtocolTypeRouter({
  'http' : get_asgi_application(),
  'websocket' : AuthMiddlewareStack(
      URLRouter(
        chat.routing.websocket_urlpatterns
        )
    ),
})