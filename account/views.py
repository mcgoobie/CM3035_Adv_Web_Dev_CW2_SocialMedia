# I Wrote this Code
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage

import os
import cv2
import json
import base64
import requests
from datetime import datetime 
from django.core import files

from account.forms import *
from account.models import *
from friends.models import *
from friends.utils import *
from friends.friend_req_status import *

TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"


# Create your views here.

# Register/Login/Logout
def register_view(request, *args, **kwargs):
    user = request.user

    # Is user is already authenticated
    if user.is_authenticated:
        return HttpResponse(f"You are already authenticated as {user.email}")
    context = {}

    # if request is a valid POST
    if request.POST:
        form = RegisterForm(request.POST)
        if form.is_valid():
            # execute functions in form.save
            form.save()
            email = request.POST['email'].lower()
            password = request.POST['password2']
            f_name = request.POST['f_name']
            l_name = request.POST['l_name']
            gender = request.POST['gender']
            dob = request.POST['dob']
            account = authenticate(email=email, password=password)

            login(request, account)
            destination = get_redirect_if_exists(request)

            if destination:  # if destination is not invalid
                return redirect(destination)
            return redirect('home')
        else:
            context['register_form'] = form

    return render(request, 'account/register.html', context)


def login_view(request, *args, **kwargs):
    context = {}

    user = request.user
    if user.is_authenticated:
        return redirect('home')

    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                destination = get_redirect_if_exists(request)
                if destination:
                    return redirect(destination)
                return redirect('home')
        else:
            context['login_form'] = form

    return render(request, 'account/login.html', context)


def get_redirect_if_exists(request):
    redirect = None
    if request.GET:
        if request.GET.get('next'):
            redirect = str(request.GET.get('next'))
    return redirect


def logout_view(request):
    logout(request)
    return redirect('home')


# View User Profile/Posts
def profile_view(request, *args, **kwargs):
    context = {}
    # Fetch current user id in profile link
    user_id = kwargs.get("user_id")

    try:
        user_account = UserAccount.objects.get(pk=user_id)
        print(user_account)
    except UserAccount.DoesNotExist:
        return HttpResponse("The user you are searching for does not exist.")

    if user_account:
        context = {
            'id': user_account.id,
            'f_name': user_account.f_name,
            'l_name': user_account.l_name,
            'gender': user_account.gender,
            'dob': user_account.dob,
            'username': user_account.username,
            'email': user_account.email,
            'profile_picture': user_account.profile_picture
        }

        # Fetch User Posts
        user_posts = UserPosts.objects.filter(
            user_account=user_account).order_by('-post_date')
        context['user_posts'] = user_posts

        new_post_form = PostForm()  # Empty Form

        if request.method == 'POST':
            new_post_form = PostForm(
                request.POST or None, request.FILES or None)

            if new_post_form.is_valid():
                # Save post to db and get the author (logged in user)
                post = new_post_form.save(commit=False)
                post.user_account = user_account
                post.save()
                new_post_form = PostForm()  # Empty Form
                context['new_post_form'] = new_post_form
        else:
            # Display blank form
            new_post_form = PostForm()
            context['new_post_form'] = new_post_form

        try:
            friend_list = FriendList.objects.get(user=user_account)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=user_account)
            friend_list.save()
        friends = friend_list.friends.all()
        context['friends'] = friends

    # Define state of profile
    is_own = True
    is_friend = False
    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
    friend_requests = None
    user = request.user

    # Profile is not logged in user if,
    #   - User is logged in, but fetched account is not the logged in users,
    #   - User is not logged in.
    if user.is_authenticated and user != user_account:
        is_own = False
        if friends.filter(pk=user.id):  # Check if friends w/ logged in user
            is_friend = True
        else:
            is_friend = False

            # 1 : User is on the receiving end of a friend request(THEN_SENT_TO_YOU)
            if get_friend_request_or_false(sender=user_account, receiver=user) != False:
                request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                context['pending_friend_request_id'] = get_friend_request_or_false(
                    sender=user_account, receiver=user).id

            # 2 : User sent a friend request
            elif get_friend_request_or_false(sender=user, receiver=user_account) != False:
                request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value

            # 3 : No Friend Request sent
            else:
                request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

    elif not user.is_authenticated:
        is_own = False

    else:
        try:
            friend_requests = FriendRequest.objects.filter(
                receiver=user, is_active=True)  # Return all active friend requests
        except:
            pass

    context['is_own'] = is_own
    context['is_friend'] = is_friend
    context['BASE_URL'] = settings.BASE_DIR
    context['request_sent'] = request_sent
    context['friend_requests'] = friend_requests

    return render(request, 'account/profile.html', context)


# User search function
def user_search_view(request):
    context = {}
    if request.method == "GET":
        search_query = request.GET.get("q")
        if len(search_query) > 0:
            # filter for distinct username containing the query
            search_results = UserAccount.objects.filter(
                username__icontains=search_query).distinct()
            user = request.user
            accounts = []  # [(account1, True), (account2, False), ...]

            if user.is_authenticated:
                # get auth user friend list
                auth_user_friend_list = FriendList.objects.get(user=user)
                for account in search_results:
                    accounts.append(
                        (account, auth_user_friend_list.is_mutual_friend(account)))
                context['accounts'] = accounts
            else:
                for account in search_results:
                    accounts.append((account, False))
            context['accounts'] = accounts

    return render(request, "account/search.html", context)


# Edit User Profile and Crop Profile Picture
def edit_profile_view(request, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login")
    user_id = kwargs.get("user_id")

    try:
        account = UserAccount.objects.get(pk=user_id)
    except UserAccount.DoesNotExist:
        return HttpResponse("Oops! Something went wrong! ")
    if account.pk != request.user.pk:
        return HttpResponse("You cannot edit someone elses' profile!")

    context = {}

    if request.POST:
        form = AccountUpdateForm(
            request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            # Update changes and redirect to profile page
            form.save()
            return redirect("account:profile", user_id=account.pk)
        else:
            # if invalid post data, reset to initial data.
            form = AccountUpdateForm(request.POST, instance=request.user,
                                     initial={
                                         "id": account.pk,
                                         "email": account.email,
                                         "username": account.username,
                                         "profile_picture": account.profile_picture,
                                         "f_name": account.f_name,
                                         "l_name": account.l_name,
                                         "gender": account.hide_email
                                     }
                                     )
            context['form'] = form
    else:  # If GET req
        # if invalid post data, reset to initial data.
        edit_form = AccountUpdateForm(
            initial={
                "id": account.pk,
                "email": account.email,
                "username": account.username,
                "profile_picture": account.profile_picture,
                "f_name": account.f_name,
                "l_name": account.l_name,
                "gender": account.hide_email
            }
        )
        context['edit_form'] = edit_form
    # max size allowed for img
    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE

    return render(request, 'account/edit_profile.html', context)


def save_temp_profile_image_from_base64String(imgString, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect Padding"
    try:
        if not os.path.exists(settings.TEMP):
            os.mkdir(settings.TEMP)
        # Each User should have a temp directory for cropping img unique to them
        if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
            os.mkdir(settings.TEMP + "/" + str(user.pk))
        url = os.path.join(settings.TEMP + "/" +
                           str(user.pk), TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(imgString)
        with storage.open('', 'wb+') as destination:
            destination.write(image)
            destination.close()

        return url

    except Exception as e:
        print('exception: ' + str(e))
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            imgString += "=" * ((4 - len(imgString) % 4) % 4)
            return save_temp_profile_image_from_base64String(imgString, user)

    return None


def crop_image(request, *args, **kwargs):
    payload = {}
    user = request.user

    if request.POST and user.is_authenticated:
        try:
            imgString = request.POST.get("image")
            url = save_temp_profile_image_from_base64String(imgString, user)
            img = cv2.imread(url)

            cropX = int(float(str(request.POST.get("cropX"))))
            cropY = int(float(str(request.POST.get("cropY"))))
            cropWidth = int(float(str(request.POST.get("cropWidth"))))
            cropHeight = int(float(str(request.POST.get("cropHeight"))))

            # Bug with cropperJS library, somtimes cropper could get to -1 coord.
            if cropX < 0:
                cropX = 0
            if cropY < 0:
                cropY = 0

            crop_img = img[cropY:cropY + cropHeight, cropX:cropX + cropWidth]

            cv2.imwrite(url, crop_img)

            user.profile_picture.delete()

            user.profile_picture.save(
                "profile_picture.png", files.File(open(url, "rb")))
            user.save()

            payload['result'] = 'success'
            payload['cropped_profile_picture'] = user.profile_picture.url

            os.remove(url)

        except Exception as e:
            payload['result'] = "error"
            payload['exception'] = str(e)

    return HttpResponse(json.dumps(payload), content_type="application/json")

# End of code I wrote