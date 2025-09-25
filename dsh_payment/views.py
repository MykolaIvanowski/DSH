import json
import uuid
from datetime import datetime
from django.utils import timezone

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from requests.auth import HTTPBasicAuth

from dsh_payment.forms import PaymentForm, DeliveryForm
from dsh_payment.models import Order, OrderItem, OrderLog
from cart.cart import Cart
from django.contrib import messages
#from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from django.conf import settings
import requests

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
        return render(request, "no_delivered_dashboard.html", {"orders":orders})
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
        return render(request, "delivered_dashboard.html",  {"orders":orders})
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
            'cancel_return': 'http://{}{}'.format(host,reverse('payment_failed'))
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
                  {"cart_products":cart.get_products(), "cart_quantities": cart.get_quantities(),
                   "totals":cart.cart_total_products(), "delivering_form":delivery_form})

def payment_failed(request):
    return render(request,"payment_failed.html", {})

def payment_success(request):
    for key in list(request.session.keys()):
        if key == 'session_key':
            del request.session[key]
    return render(request, "payment_success.html", {})


#TODO where to put, I gues settings
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'

def get_access_token():
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-language": "en-US"}
    data = {"grand_type": "client_credentials"}
    response = requests.post(url=url, headers=headers,data=data, auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET))
    return response.json()["access_token"]

def create_order():
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-language": "en-US"}
    payload = {
        "intend" :"CAPTURE",
        "purchase_units":[{
            "amount": {
                "currency_code":"USD",
                "value":str("amount")
            }
        }]
    }
    response = requests.post(url=url, headers=headers,json=payload)
    return response.json()

def billing_view(request):
    cart = Cart(request)
    quantity = cart.get_quantities()
    totals = cart.cart_total_products()
    cart_products = cart.get_products()
    if request.method == 'POST':
        payment_form = PaymentForm(requests or None)
        if payment_form.is_valid():
            access_token =  get_access_token()
            order = create_order(access_token, payment_form.cleaned_data['amount'])
            approval_url = next(link['href'] for link in order['links'] if link['rel']=='approve')
            return redirect(approval_url)
        else:
            payment_form = PaymentForm()
            return render(requests, 'billing_info.html',{"cart_products":cart_products,
                                                         "quantities":quantity,"totals":totals,
                                                         "delivery_info":requests.POST, "billing_form":payment_form} )


def paypal_webhook(request):
    if request.method == "POST":
        data = json.loads(request.body)
        event_type = data.get("event_type")
        if event_type == "CHECKOUT.ORDER.APPROVED":
            order_id = data["resource"]["id"]
            #TODO set or removed
        elif event_type == "PAYMENT.CAPTURE.COMPLETED":
            amount = data["resource"]["amount"]["value"]
            #TODO set to db and
        return JsonResponse({"status":"received"})

def paypal_success(request):
    order_id =  request.GET.get('token')
    access_token = get_access_token()
    response = request.post(f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture',
                            headers = {'Content-Type':'application/json', 'Authorization':f'Bearer {access_token}'})
    data =response.json()
    return render(request, "payment_success.html",{})


def confirm_order_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    # check avalability for products
    for item in order.items.all():
        if item.product.stock < item.quantity:
            messages.error(request, f"Недостатньо товару: {item.product.name}")
            return redirect('order_detail', order_id=order.id)

    # update storage
    for item in order.items.all():
        item.product.stock -= item.quantity
        item.product.save()

    # update status
    order.delivered = True
    order.date_delivered = timezone.now()
    order.save()

    # Логування
    OrderLog.objects.create(order=order, status='delivered', note='Замовлення підтверджено')

    messages.success(request, "Замовлення підтверджено та склад оновлено")
    return redirect('order_list')


def order_dashboard_view(request):
    status_filter = request.GET.get('status')
    orders = Order.objects.all()

    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, 'orders/dashboard.html', {'orders': orders})

def update_order_status_view(request, order_id, new_status):
    order = get_object_or_404(Order, pk=order_id)

    if order.status != new_status:
        order.status = new_status
        if new_status == 'delivered':
            order.date_delivered = timezone.now()
        order.save()

        OrderLog.objects.create(order=order, status=new_status, note=f'Status changed to {new_status}')
        messages.success(request, f'Статус замовлення #{order.id} оновлено до {new_status}')

    return redirect('order_dashboard')

