from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Product
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def about(request):
    return render(request, 'about.html', {})


def home(request):
    products = Product.objects.all()
    return render(request,'home.html', {'products': products})


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username,password=password)

        if user is not None:
            login(request, user)

            messages.success(request, 'You have been login')
            return render(request, 'login.html',{})
        else:
            messages.success(request,'There was an error')
            return redirect('login')
    else:
        return render(request, 'login.html', {'error':'invalid credential'})

def logout_user(request):
    logout(request)
    messages.success(request,'You have been logout')
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form=