from django.db import models
from django.conf import settings

# Create your models here.


# class ChatRoom(models.Model):
#     # Chat Room title must be unique
#     title = models.CharField(max_length=50, unique=True, blank=False)
#     # M-T-M Rel. as there can be many users with access to many chatrooms
#     users = models.ManyToManyField(
#         settings.AUTH_USER_MODEL, blank=True, help_text="chatroom users")

#     def __str__(self):
#         return self.title
    
#     def connect_user(self, user):
#         # Return true if user successfully connected to chatroom
#         is_user_added = False

#         if not user in self.users.all():
#             self.users.add(user)
#             self.save()
#             is_user_added = True
#         elif user in self.users.all():
#             is_user_added = True
#         return is_user_added
    
#     def disconnect_user(self, user):
#         # Return True if user successfully disconnected from chatroom
#         is_user_removed = False

#         if user in self.users.all():
#             self.users.remove(user)
#             self.save()
#             is_user_removed = True
#         return is_user_removed
    

#     @property
#     def group_name(self):
#         # Returns channel group name that socket is suscribed to and get sent messages when generated.
#         return f"ChatRoom-{self.id}"
    

# class ChatRoomMessageManager(models.Manager):
#     def by_room(self, room):
#         q_set = ChatRoomMessages.objects(room=room).order_by('-timestamp')
#         return q_set

# class ChatRoomMessages(models.Model):
#     # Chat messages created by users inside the chat rooms. (FK)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     content = models.TextField(unique=False, blank=False)

#     def __str__(self):
#         return self.content