# Start of code I wrote
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

from account.models import *
from friends.models import *
# Create your views here.


def home_screen_view(request):
    user = request.user
    all_friends_posts = []
    context = {}
    if user.is_authenticated:
        try:
            friend_list = FriendList.objects.get(user=user)
            # Home page should display all recent posts made by all your friends
            for friend in friend_list.friends.all():
                friend_posts = UserPosts.objects.filter(
                    Q(user_account=friend) & ~Q(user_account=user)).order_by('-post_date')
                all_friends_posts.append(friend_posts)

            # Check for number of friends, template will change depending on if they exist or not.
            context['no_friends'] = len(all_friends_posts)
            context['all_friends_posts'] = all_friends_posts
        except FriendList.DoesNotExist:
            # If user has no friends yet, show default home page
            context['no_friends'] = 0
            context['all_friends_posts'] = all_friends_posts

        return render(request, "home.html", context)
    else:
        return render(request, "home.html", context)

# End of code I wrote