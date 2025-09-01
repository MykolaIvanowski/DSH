from datetime import datetime
from statistics import quantiles

from django.shortcuts import render,redirect

from dsh_payment.forms import PaymentForm
from dsh_payment.models import Order, OrderItem
from cart.cart import Cart
from django.contrib import messages


# Create your views here.
def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)
        items = OrderItem.objects.filters(order=pk)

        if request.POST:
            status = request.POST['delivering_status']

            if status =='true':
                order = Order.objects.filter(order=pk)
                date_now = datetime.now()
                order.update(delivered = True, date_delivered = date_now)
            else:
                order = Order.objects.filters(id=pk)
                order.update(deliverd=False)
            messages.success('Order status updated')
            return redirect('Home')
        return render(request, 'orders.html', {'order': order, 'items': items})

def not_delivered_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(delivered=False)
        if request.POST:
            # status = request.POST['delivered_status']
            num = request.POST['num']
            order = Order.objects.filters(id=num)
            time_now = datetime.now()
            order.update(deliverd=True, date_delivered = time_now)
            messages.success(request, 'Delivery status updated')
            return redirect('home') #TODO redirect home?
        return render(request, "not_delivered.html", {"orders":orders})
    else:
        messages.success(request, 'Access denied')
        return redirect('home')
def delivered_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objetcs.filter(delivered = True)
        if request.POST:
            # status = request.POST['delivered_satus']
            num = request.POST['num']
            order = Order.objects.filters(id=num)
            # time_now = datetime.now()
            order.update(delivered = False)
            messages.success(request, 'Delivery status updated')
            return redirect('home') #TODO redirect home?
        return render(request, "delivered.html",  {"orders":orders})
    else:
        messages.success(request, "Access denied")
        return redirect('home')
def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_products()
        quantity = cart.get_quantities()
        total = cart.cart_total_products()

        payment_form = PaymentForm(request.POST or None)
        my_delivery = request.session.get('my_delivery')
def billing_info(request):
    pass
def checkout(request):
    pass
def payment_failed(request):
    pass
def payment_success(request):
    pass