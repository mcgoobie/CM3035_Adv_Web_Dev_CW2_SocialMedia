# Start of code I wrote
from django.urls import path

from account.views import *

app_name = 'account'

urlpatterns = [
    path('<user_id>/', profile_view, name="profile"),
    path('<user_id>/edit/', edit_profile_view, name="edit"),
    path('<user_id>/edit/cropImage/', crop_image, name="crop_image"),
]

# End of code I wrote
