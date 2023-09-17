
from django.urls import path , include
from chat.consumer import *
 
# Route to the URL ChatConsumer (ASGI : Async Server Getway Interface)
websocket_urlpatterns = [
    path("" , ChatConsumer.as_asgi()) ,
]