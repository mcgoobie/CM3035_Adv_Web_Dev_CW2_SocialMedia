from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout

# Create your views here.


def chat_view(request, *args, **kwargs):
	if not request.user.is_authenticated:
		return HttpResponse('You have to be logged in to chat.')
	else:
		context = {}
		return render(request, 'chat/chat.html', context)
