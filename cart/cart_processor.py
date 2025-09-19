from .cart import Cart

def cart(request):
    cart = Cart(request)
    return { 'cart' : cart, 'cart_total_quantity': cart.get_total_quantity()}
