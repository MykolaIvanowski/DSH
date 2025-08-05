from django.http import HttpResponse
from django.shortcuts import render
from .models import Product
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def index(request):
    data = Product.objects.all()
    return  render(request, 'index_template.html', {'data':data})


def about(request):
    return render(request, 'about.html', {})


def home(request):
    products = Product.objects.all()
    return render(request,'home.html', {'products': products})


def login_user(request):
    return render(request, 'login.html',{})

def logout_user(request):
    pass