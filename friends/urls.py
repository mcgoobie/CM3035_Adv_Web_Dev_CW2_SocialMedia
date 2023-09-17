# Start of code I wrote
from django.urls import path
from friends.views import *

app_name = "friends"

urlpatterns = [
    path('list/<user_id>/', friend_list_view, name='friend_list'),
    path('friend_request/', send_friend_request_view, name='friend_request'),
    path('friend_request/<user_id>/', friend_requests_view, name='friend_requests'),
    path('accept_friend_request/<friend_request_id>', accept_friend_request_view, name='friend_request_accept'),
    path('decline_friend_request/<friend_request_id>', decline_friend_request_view, name='friend_request_decline'),
    path('remove_friend/', remove_friend_view, name="remove_friend"),
    path('cancel_friend_request/', cancel_friend_request_view, name="friend_request_cancel")
]

# End of code I wrote