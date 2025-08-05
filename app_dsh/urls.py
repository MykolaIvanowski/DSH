from tkinter.font import names

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("home/", views.home, name="home"),
    path("login/", views.login_user, name='login'),
    path("logout", views.logout_user, name='logout')
]
