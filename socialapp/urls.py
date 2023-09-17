# Start of code I wrote

from django.urls import path
from socialapp.views import *

app_name = 'home'

urlpatterns = [
    path('', home_screen_view, name="home"),
]

# End of code I wrote
