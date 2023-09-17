# Start of code I wrote
from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.


class FriendList(models.Model):
    # Friend List (1 : user/owner, 2 : user friend list)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")  # User Associated Friend List
    friends = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="friends")  # List of friends the user has

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        # Add a new friend
        if not account in self.friends.all():
            # Check if account exists in friend list, if not add
            self.friends.add(account)
            self.save()

    def del_friend(self, account):
        # delete a friend
        if account in self.friends.all():
            # Check if account exists in friend list, if not add
            self.friends.remove(account)
            self.save()

    def unfriend(self, removee):
        # initiate unfriending someone
        remover_friends_list = self  # Friend's list of person removing someone
        # Remove friend from initiator's friend list
        remover_friends_list.del_friend(removee)
        # Remove yourself from their freinds list
        friends_list = FriendList.objects.get(user=removee)
        friends_list.del_friend(remover_friends_list.user)

    def is_mutual_friend(self, friend):
        # Are mutuals
        if friend in self.friends.all():
            return True
        return False


class FriendRequest(models.Model):
    # Friend Request (1 : Sender, 2 : Receiver)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver")
    is_active = models.BooleanField(blank=True, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sender.username

    def accept(self):
        # Accept a Friend request - Update sender and receiver friend lists
        receiver_fl = FriendList.objects.get(user=self.receiver)
        if receiver_fl:
            receiver_fl.add_friend(self.sender)

            sender_fl = FriendList.objects.get(user=self.sender)
            if sender_fl:
                sender_fl.add_friend(self.receiver)
                self.is_active = False
                self.save()

    def decline(self):
        # Decline friend request
        self.is_active = False
        self.save()

    def cancel(self):
        # Cancel Friend Request
        self.is_active = False
        self.save()

# End of Code I wrote