import uuid
from datetime import datetime
from statistics import quantiles

from django.shortcuts import render,redirect

from dsh_payment.forms import PaymentForm, DeliveryForm
from dsh_payment.models import Order, OrderItem
from cart.cart import Cart
from django.contrib import messages
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from django.conf import settings

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
        cart_products = cart.get_products
        quantity = cart.get_quantities
        total = cart.cart_total_products()

        payment_form = PaymentForm(request.POST or None)
        my_delivering = request.session.get('my_delivering')
        full_name = my_delivering['delivery_full_name']
        email = my_delivering['delivery_email']
        delivery_address = (f'{my_delivering['delivery_address1']}'
                            f'\n{my_delivering['delivery_address2']}\n{my_delivering['delivery_city']}'
                            f'\n{my_delivering['delivery_state']}\n{my_delivering['delivery_zipcode']}'
                            f'\n{my_delivering['delivery_country']}\n')

        create_order = Order(full_name=full_name,email=email, delivery_address=delivery_address, amount_paid=total)
        order_id = create_order.pk

        for product in  cart_products():
            product_id= product.id
            if product.is_sale:
                price = product.sale_price
            else:
                price = product.price

            for key, value in quantity().items():
                if int(key) == product.id:
                    create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                    create_order_item.save()

        for key in list(request.session.keys()):
            if key == 'session_key':
                del request.session[key]
        messages.success(request, 'Order placed')
        return redirect('home')
    else:
        messages.success('Access denied')
        return redirect('home')
def billing_info(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_products
        quantity = cart.get_quantities
        totals = cart.cart_total_products()
        my_delivery = request.POST
        request.session['my_delivering'] = my_delivery

        host = request.get_host()

        paypal_dict = {
            'business':settings.PAYPAL_RESIVER_EMAIL,
            'amount':totals,
            'item_name':'Book Order',
            'no_shipping': '2',
            'invoice': str(uuid.uuid4()),
            'currency_code': 'UDS',
            'notify_url':'http://{}{}'.format(host, reverse('paypal-ipn')),
            'return_url': 'http://{}{}'.format(host, reverse('payment_success')),
            'cancel_return': 'http://{}{}'.format(host,reverse('payment_faile'))
        }
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)
        billing_form = PaymentForm()
        return render(request, 'billing_info.html',
                      {"paypal_form":paypal_form, "cart_products":cart_products, "quantities":quantity,
                       "totals":totals, "delivery_info":request.POST, "billing_form":billing_form})
    else:
        messages.success('Access denied')
        return redirect('home') #TODO redirect home?
def checkout(request):
    cart = Cart(request)
    delivery_form = DeliveryForm(request.POST or None)
    return render(request, "checkout.html",
                  {"cart_products":cart.get_products(), "quantities": cart.get_quantities(),
                   "totals":cart.cart_total_products(), "delivering_form":delivery_form})
def payment_failed(request):
    return render(request,"payment_failed.html", {})

def payment_success(request):
    for key in list(request.session.keys()):
        if key == 'session_key':
            del request.session[key]
    return render(request, "payment_success.html", {})