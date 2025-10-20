from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("home/", RedirectView.as_view(url='/', permanent=False), name="home_redirect"),
    path("about/", views.about, name="about"),
    path("login/", views.login_user, name='login'),
    path("logout/", views.logout_user, name='logout'),
    path("product/<int:id>", views.product_detail, name='product_detail'),
    path("category/<str:category_name>/", views.home, name='category'),
    path("search/", views.search, name='search')
]
