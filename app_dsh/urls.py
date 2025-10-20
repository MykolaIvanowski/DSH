from tkinter.font import names

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("index/", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("home/", views.home, name="home"),
    path("login/", views.login_user, name='login'),
    path("logout/", views.logout_user, name='logout'),
    path("product/<int:id>", views.product_detail, name='product_detail'),
    path("category_description/", views.category, name='category_description'),
    path("category/<str:category_name>/", views.home, name='category'),
    path("search/", views.search, name='search')
]
