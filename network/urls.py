
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    # my routes
    path("profile/<str:username>", views.profile, name="profile"),
    path("profile/<str:username>/unfollow", views.unfollow, name="unfollow"),
    path("profile/<str:username>/follow", views.follow, name="follow"),
    path("following", views.following, name="following"),
    # API Routes
    path("posts", views.posts, name="posts"),
    path("edit/<int:id>", views.edit, name="edit"),
    path("like/<int:id>", views.like, name="like"),
    path("unlike/<int:id>", views.unlike, name="unlike")
]
