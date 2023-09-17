# Start of Code I Wrote
from django.shortcuts import render, redirect
from django.http import HttpResponse
import json

from account.models import *
from friends.models import *
# Create your views here.

"""
View a Friend List
"""
def friend_list_view(request, **kwargs):
    context = {}
    user = request.user

    if user.is_authenticated:
        user_id = kwargs.get('user_id')

        # Own friend list
        if user_id:
            try:
                active_user = UserAccount.objects.get(pk=user_id)
                context['active_user'] = active_user
            except UserAccount.DoesNotExist:
                return HttpResponse('User does not exist. ')
            try:
                friend_list = FriendList.objects.get(user=active_user)
            except FriendList.DoesNotExist:
                return HttpResponse(f'Could not find a friend list for {active_user.username}')

        # Friend's friend list
        if user != active_user:
            if not user in friend_list.friends.all():
                return HttpResponse('You must be friend to view their friends list.')

        friends = []
        auth_user_friend_list = FriendList.objects.get(user=user)

        for friend in friend_list.friends.all():
            # Check if you are friends with seperate user
            friends.append(
                (friend, auth_user_friend_list.is_mutual_friend(friend)))
        context['friends'] = friends

    else:
        return HttpResponse('You must be friend to view their friends list.')
    return render(request, 'friends/friend_list.html', context)


"""
View all pending friend requests in your account
"""
def friend_requests_view(request, **kwargs):
    # if user is logged in, check and fetch all pending friend requests
    context = {}
    user = request.user

    if user.is_authenticated:
        user_id = kwargs.get('user_id')
        user_account = UserAccount.objects.get(pk=user_id)

        if user_account == user:
            friend_requests = FriendRequest.objects.filter(
                receiver=user_account, is_active=True)
            context['friend_requests'] = friend_requests
        else:
            return HttpResponse('You do not have authentication to view other users friend requests.')
    else:
        redirect('login')
    return render(request, 'friends/friend_request.html', context)


"""
Send Friend Request to another user view
"""
def send_friend_request_view(request):
    user = request.user
    payload = {}

    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")
        if user_id:
            receiver = UserAccount.objects.get(pk=user_id)

            try:
                # Get all open/closed friend requests
                friend_requests = FriendRequest.objects.filter(
                    sender=user, receiver=receiver)

                # Get all open requests
                try:
                    for request in friend_requests:
                        if request.is_active:
                            raise Exception(
                                "You already sent them a friend request. ")
                    # if none active, create new request
                    friend_request = FriendRequest(
                        sender=user, receiver=receiver)
                    friend_request.save()
                    payload['response'] = 'Friend request has been sent.'
                except Exception as e:
                    payload['response'] = str(e)
            except FriendRequest.DoesNotExist:
                # No friend requests
                friend_request = FriendRequest(sender=user, receiver=receiver)
                friend_request.save()
                payload['response'] = 'Friend request has been sent.'

            if payload['response'] == None:
                payload['response'] = 'Something went wrong.'
        else:
            payload['response'] = 'Unable to send friend request.'
    else:
        payload['response'] = 'You must be logged in to send a friend request.'

    return HttpResponse(json.dumps(payload), content_type='application/json')


"""
 3 Possible outcomes of an open friend request (Accept, Decline, Cancel)
"""
def accept_friend_request_view(request, *args, **kwargs):
    user = request.user
    payload = {}

    if request.method == 'GET' and user.is_authenticated:
        friend_request_id = kwargs.get('friend_request_id')

        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)

            if friend_request.receiver == user:  # Check if this friend request has you as the receiver
                if friend_request:  # if exists, accept it
                    friend_request.accept()
                    payload['response'] = 'You have accepted the friend request. '
                else:
                    payload['response'] = 'Something went wrong. '
            else:  # Friend request does not have user as the receiver
                payload['response'] = 'You are not the receiver of this friend request. '
        else:  # wrong friend_request_id
            payload['response'] = 'Unable to accept friend request. '
    else:
        payload['response'] = 'You must be logged in to accept friend requests. '

    print('payload info : ', payload)
    return HttpResponse(json.dumps(payload), content_type='application/json')


def decline_friend_request_view(request, *args, **kwargs):
    user = request.user
    payload = {}

    if request.method == 'GET' and user.is_authenticated:
        friend_request_id = kwargs.get('friend_request_id')

        if friend_request_id:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)

            if friend_request.receiver == user:  # Check if this friend request has you as the receiver
                if friend_request:  # if exists, decline it
                    friend_request.decline()
                    payload['response'] = 'You have declined the friend request.'
                else:
                    payload['response'] = 'Something went wrong. '
            else:  # Friend request does not have user as the receiver
                payload['response'] = 'You are not the receiver of this friend request.'
        else:  # wrong friend_request_id
            payload['response'] = 'Unable to decline friend request. '
    else:
        payload['response'] = 'You must be logged in to decline friend requests.'

    return HttpResponse(json.dumps(payload), content_type='application/json')


def cancel_friend_request_view(request):
    user = request.user
    payload = {}

    if request.method == 'POST' and user.is_authenticated:
        user_id = request.POST.get('receiver_user_id')

        if user_id:
            receiver = UserAccount.objects.get(pk=user_id)

            try:
                # Filter for active friend requests where the sender is the logged in user
                friend_requests = FriendRequest.objects.filter(
                    sender=user, receiver=receiver, is_active=True)
            except Exception as e:
                payload['response'] = 'Friend request does not exist.'

            if len(friend_requests) > 1:
                for request in friend_requests:
                    request.cancel
                payload['response'] = 'Friend Request Cancelled.'

            else:
                friend_requests.first().cancel()
                payload['response'] = 'Friend Request Cancelled.'

        else:
            payload['response'] = 'Unable to cancel the friend request.'
    else:
        payload['response'] = 'You must be authenticated to cancel a friend request.'
    return HttpResponse(json.dumps(payload), content_type='application/json')


"""
Delete/Remove an existing Friend View/Function
"""
def remove_friend_view(request):
    user = request.user
    payload = {}

    if request.method == 'POST' and user.is_authenticated:
        user_id = request.POST.get('receiver_user_id')

        if user_id:
            try:
                removee = UserAccount.objects.get(pk=user_id)
                friend_list = FriendList.objects.get(user=user)
                friend_list.unfriend(removee)

                payload['response'] = 'Successfully removed this friend.'
            except Exception as e:
                payload['response'] = f'Something went wrong: {str(e)}.'
        else:
            payload['response'] = 'There was an error and the friend could not be removed.'
    else:
        payload['response'] = 'You must be logged in to remove a friend.'

    return HttpResponse(json.dumps(payload), content_type='application/json')


# End of code I wrote