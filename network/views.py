import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Post, Follow, Like
from django.core.paginator import Paginator


def index(request):
    posts = Post.objects.all().order_by("-timestamp")
    posts = [post.serialize() for post in posts]
    liked_posts = set()
    try:
        likes = Like.objects.filter(user=request.user)
        for like in likes:
            liked_posts.add(like.post.id)
    except:
        pass

    p = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)
    return render(
        request, "network/index.html", {"posts": page_obj, "likes": liked_posts}
    )


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required(login_url="login")
def posts(request):
    if request.method == "POST":
        content = request.POST["content"]
        post = Post(creator=request.user, content=content)
        post.save()
        return HttpResponseRedirect(reverse("index"))


def profile(request, username):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(creator=user).order_by("id").reverse()
    posts = [post.serialize() for post in posts]

    p = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)

    following_user = user.user_followed.filter(user=request.user).exists() if request.user.is_authenticated else False

    return render(
        request,
        "network/profile.html",
        {
            "username": username,
            "followers": user.user_followed.count(),
            "following": user.user_following.count(),
            "posts": page_obj,
            "toggle": request.user.is_authenticated and request.user != user,
            "following_user": following_user,
        },
    )


@login_required(login_url="login")
def unfollow(request, username):
    user = User.objects.get(username=username)
    f = Follow.objects.filter(user=request.user, user_follower=user)
    f.delete()

    return HttpResponseRedirect(reverse("profile", args=(username,)))


@login_required(login_url="login")
def follow(request, username):
    user = User.objects.get(username=username)
    f = Follow.objects.create(user=request.user, user_follower=user)
    f.save()

    return HttpResponseRedirect(reverse("profile", args=(username,)))


@login_required(login_url="login")
def following(request):
    following = Follow.objects.filter(user=request.user)
    users = set()
    for f in following:
        users.add(f.user_follower)
    posts = Post.objects.filter(creator__in=users).order_by("id").reverse()
    posts = [post.serialize() for post in posts]

    p = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = p.get_page(page_number)

    return render(request, "network/following.html", {"posts": page_obj})


@csrf_exempt
def edit(request, id):
    if request.method == "PUT":
        try:
            post = Post.objects.get(pk=id, creator=request.user)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)

        data = json.loads(request.body)
        if data.get("post") is not None:
            post.content = data["post"]

        post.save()
        return HttpResponse(status=204)


@csrf_exempt
@login_required(login_url="login")
def like(request, id):
    if request.method == "PUT":
        post = Post.objects.get(pk=id)
        l = Like.objects.create(user=request.user, post=post)
        l.save()
        return JsonResponse({"message": "Success"}, status=201)


@csrf_exempt
@login_required(login_url="login")
def unlike(request, id):
    if request.method == "PUT":
        post = Post.objects.get(pk=id)
        l = Like.objects.get(user=request.user, post=post)
        l.delete()
        return HttpResponse(status=204)
