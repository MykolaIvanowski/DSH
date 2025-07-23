from django.http import HttpResponse
from django.shortcuts import render
from .models import Product


def index(request):
    data = Product.objects.all()
    return  render(request, 'index_template.html', {'data':data})


def about(request):
    return HttpResponse("<h3>about page</h3>")


def home(request):
    products = Product.objects.all()
    return render(request,'home.html', {'products': products})
