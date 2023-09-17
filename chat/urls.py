# Start of code I wrote
from django.urls import path, include
from chat.views import *

app_name = 'chat'

urlpatterns = [
    path('', chat_view, name="chat"),
]
# End of code I wrote