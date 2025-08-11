from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Product
from .forms import RegistrationForm
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
    form = RegistrationForm()
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data('username')
            password = form.cleaned_data('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Username created - please filed out of you user info below"))
            return redirect('updated_info')
        else:
            messages.success(request, ("Whoops there was a problem registration, please try again..."))
            return redirect('register')
    else:
        return render(request, 'register.html', {'form':form})


def product_detail(request, id):
    product = Product.objects.get(id=id)
    return render(request, 'product_detail.html', {'product': product})