from django.http import HttpResponse
from django.shortcuts import render
from .models import Product

dummy_datas = [{"data1": "one", "data2": "two"}, {"data1": "one", "data2": "two"}]
context = {"dummy_datas": dummy_datas}


def index(request):
    data = Product.objects.all()
    return  render(request, 'index_template.html', {'data':data})


def about(request):
    return HttpResponse("<h3>about page</h3>")

