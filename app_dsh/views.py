from django.http import HttpResponse
from django.shortcuts import render

dummy_datas = [
    {
        "data1": "one",
        "data2": "two"
    },
    {
        "data1": "one",
        "data2": "two"
    }
]
context = {'dummy_datas': dummy_datas}

def index(request):
    return render(request, "base/index.html", context)


def about(request):
    return HttpResponse("<h3>about page</h3>")

