from django.http import HttpResponse
from django.shortcuts import render, redirect
from unicodedata import category

from .models import Product, Category
from .forms import RegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q

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

def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        searched =Product.objects.filter(Q(name__icontains=searched),Q(description__icontains=searched))
        if not searched:
            messages.success(request, 'That products does not exist')
            return render(request, "search.html", {})
        else:
            return render(request, 'search.html', {'searched': searched})
    else:
        return render(request, "search.html",{})

def category_description(request):
    categories = Category.objects.all()
    return render(request, 'category_description',{'categories':categories})
def category(request, category_name):
    pass