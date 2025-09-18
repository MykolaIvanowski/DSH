from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .cart import Cart
from app_dsh.models import Product
# Create your views here.

def cart_basic(request):
    cart = Cart(request)
    cart_products = cart.get_products
    quantities = cart.get_quantities
    totals = cart.cart_total_products()
    return render(request, "cart.html",
                  {'cart_products': cart_products, "cart_quantities": quantities, "totals": totals} )

def cart_add(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_quantities = int(request.POST.get('product_qty'))

        product = get_object_or_404(Product,id = product_id)
        cart.add_product(product=product, quantity=product_quantities)
        cart_quantity = cart.__len__()

        response = JsonResponse({'quantity': cart_quantity})
        messages.success(request, ("Product added to cart"))
        return response


def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') =='post':
        product_id = request.POST.get('product_id')
        cart.delete_from_cart(product_id)

        response =JsonResponse({'product':product_id})
        messages.success(request, ("Item delete from shopping cart"))
        return response


def cart_update(request):
    cart = Cart(request)

    if request.POST.get('action') =='post':
        product_id =int(request.POST.get('product_id'))
        product_quantity = int(request.POST.get('product_quantity'))

        cart.update_cart(product_id, product_quantity)

        response = JsonResponse({'quantity':product_quantity})
        messages.success(request, ("Your cart has been updated"))
        return response