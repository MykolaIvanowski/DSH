from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import Product, Category
from .forms import RegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q

def about(request):
    return render(request, 'about.html', {})


def home(request, category_name=None):
    if category_name:
        category = Category.objects.filter(name=category_name).first()
        products = Product.objects.filter(category=category.id)

    else:
        products = Product.objects.all()

    products = products.order_by('-stock')
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    categories = Category.objects.all()
    return render(request,'home.html', {'products': page_object.object_list, 'categories': categories,
                                        'selected_category': category_name, 'page_object':page_object})


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
            messages.error(request,'Invalid username or password')
            return redirect('login')
    else:
        return render(request, 'login.html', {'error':'invalid credential'})

def logout_user(request):
    if not (request.user.is_authenticated and request.user.is_superuser):
        logout(request)
        messages.success(request,'You have been logout')
    return redirect('home')


def product_detail(request, id):
    product = Product.objects.get(id=id)
    return render(request, 'product_detail.html', {'product': product})


def search(request):
    query = request.POST.get('searched') or request.GET.get('searched')
    products = Product.objects.all()

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        if not products.exists():
            messages.warning(request, 'No products found for your search.')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {
        'products': page_obj.object_list,
        'page_object': page_obj,
        'categories': Category.objects.all(),
        'selected_category': None,
        'searched': query,
    })
