from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Product
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})
def login_user(request):
    if request.method == 'POST':
        username = request.POST('username')
        password = request.POST('password')
