"""all backend goes here"""
import urllib
import os
import requests
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError


access_token = os.environ.get("access_token")
if access_token is None:
    raise RuntimeError(
        'api key not set.\nSetting: export access_token="YOUR_ACCESS_TOKEN_HERE"'
    )
BASE_URL = "https://graph.facebook.com"


# Create your views here
def index(request):
    """displays the landing page of the application"""
    context = {
        "title": "home",
        "users": User.objects.all(),
    }
    return render(request, "base/index.html", context)


def login_view(request):
    """logs a user in"""
    context = {
        "title": "login",
    }
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("base:index"))
        messages.error(request, "Invalid credentials")
    return render(request, "base/authenticate.html", context)


def logout_view(request):
    """logs a user out"""
    logout(request)
    return HttpResponseRedirect(reverse("base:index"))


def register(request):
    """adds a user to db and logs the user in into current session"""
    context = {
        "title": "register",
    }
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.create_user(
                username=username, password=password, email="someone@example.com"
            )
        except IntegrityError:
            messages.error(request, "Username already taken")
        else:
            login(request, user)
            return HttpResponseRedirect(reverse("base:index"))
    return render(request, "base/authenticate.html", context)


def add_comment(request, post_id):
    """adds a comment to post with request id"""
    if request.method == "POST":
        comment = request.POST.get("message")
        comment = urllib.parse.quote(comment)
        page_id = request.POST.get("id")
        response = requests.post(
            f"{BASE_URL}/{post_id}/comments/?message={comment}&access_token={access_token}"
        )
        response.raise_for_status()
        response = response.json()
        print(response)
        messages.success(request, "comment published successfully.")
    return HttpResponseRedirect(f"/?id={page_id}")
