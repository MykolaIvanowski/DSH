import json
import uuid
from datetime import datetime
from django.utils import timezone

from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from requests.auth import HTTPBasicAuth

from dsh_payment.forms import PaymentForm, DeliveryForm
from dsh_payment.models import Order, OrderItem, OrderLog, STATUS_CHOICES
from cart.cart import Cart
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
import requests
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import OrderItem

# Create your views here.
def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)
        items = OrderItem.objects.filter(order=pk)

        if request.POST:
            status = request.POST['delivering_status']

            if status =='true':
                order = Order.objects.filter(order=pk)
                date_now = datetime.now()
                order.update(delivered = True, date_delivered = date_now)
            else:
                order = Order.objects.filter(id=pk)
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
            order = Order.objects.filter(id=num)
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
            order = Order.objects.filter(id=num)
            # time_now = datetime.now()
            order.update(delivered = False)
            messages.success(request, 'Delivery status updated')
            return redirect('home') #TODO redirect home?
        return render(request, "delivered_dashboard.html",  {"orders":orders})
    else:
        messages.success(request, "Access denied")
        return redirect('home')




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
    headers = {
        "Accept": "application/json",
        "Accept-language": "en-US",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url=url, headers=headers,data=data, auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET))
    if "access_token" in response.json():
        return response.json()["access_token"]
    else:
        raise ValueError(f"Access token was not found {response}")

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

def get_access_token_mock():
    return "mock_token"


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
            messages.error(request, f"Not enough products: {item.product.name}")
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


@require_http_methods(["GET", "POST"])
def order_dashboard_view(request):
    if not (request.user.is_authenticated and request.user.is_superuser):
        raise Http404('ooops.. resource not found')

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")
        print(order_id)
        if order_id and new_status:
            order = get_object_or_404(Order, pk=order_id)
            if new_status in dict(STATUS_CHOICES):
                order.status = new_status
                order.save()
                print('Order status updated')
                return redirect('dashboard')


    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')

    orders = Order.objects.all().order_by('-date_ordered')

    if status_filter:
        orders = orders.filter(status=status_filter)

    if search_query:
        orders = orders.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    paginator = Paginator(orders, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard.html', {
        'orders': page_obj,
        'status_filter': status_filter,
        'search_query': search_query
    })

def update_order_status_view(request, order_id, new_status):
    if request.user.is_authenticated and request.user.is_superuser:
        order = get_object_or_404(Order, pk=order_id)

        if order.status != new_status:
            order.status = new_status
            if new_status == 'delivered':
                order.date_delivered = timezone.now()
            order.save()

            OrderLog.objects.create(order=order, status=new_status, note=f'Status changed to {new_status}')
            messages.success(request, f'Order status #{order.id} updated to {new_status}')

        return redirect('order_dashboard')
    else:
        raise Http404('ooops.. resource not found')



def order_item_view(request, item_id):
    if request.user.is_authenticated and request.user.is_superuser:
        item = get_object_or_404(OrderItem, pk=item_id)
        order = item.order
        items = order.items.select_related('product').all()

        return render(request, 'order_items.html', {
            'order': order,
            'items': items
        })
    else:
        raise Http404('ooops.. resource not found')


def delivery_info_view(request):
    cart = Cart(request)
    cart_products = cart.get_products()
    quantity = cart.get_quantities()
    total = cart.cart_total_products()

    if request.method == 'POST':
        print('post!!!!!!!!!')
        form = DeliveryForm(request.POST)
        action = request.POST.get("action")

        if form.is_valid():
            order = form.save(commit=False)
            order.status = 'created'
            order.amount_paid = 0 if action == "pay_later" else total
            order.save()

            # Зберігаємо позиції замовлення
            for product in cart_products:
                product_id = product.id
                price = product.sale_price if product.is_sale else product.price
                qty = quantity.get(str(product_id), 1)

                OrderItem.objects.create(
                    order=order,
                    product_id=product_id,
                    quantity=qty,
                    price=price
                )

            # Очищення сесії
            request.session.pop('session_key', None)

            if action == "pay_later":
                messages.success(request, 'Order placed. Manager will contact you.')
                return render(request, 'delivery_info.html', {
                    'delivery_form': DeliveryForm(),
                    'delivery_info': order,
                    'totals': total
                })

            elif action == "pay_online":
                access_token = get_access_token_mock()
                headers = {
                    'Content-Type': "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
                order_payload = {
                    "intent": "CAPTURE",
                    "purchase_units": [{
                        "amount": {
                            "currency_code": "EUR",
                            "value": str(total)
                        }
                    }],
                    "application_context": {
                        "return_url": request.build_absolute_uri("/paypal_success/"),
                        "cancel_url": request.build_absolute_uri("/paypal_cancel/")
                    }
                }

                response = requests.post(
                    "https://api-m.sandbox.paypal.com/v2/checkout/orders",
                    headers=headers,
                    json=order_payload
                )

                data = response.json()
                for link in data.get("links", []):
                    if link['rel'] == "approve":
                        messages.success(request, 'Redirecting to PayPal...')
                        return redirect(link['href'])

                messages.error(request, 'Could not create PayPal order. Test environment.')
                return render(request, 'delivery_info.html', {
                    'delivery_form': form,
                    'totals': total
                })

        else:
            messages.error(request, 'Form is not valid.')
            return render(request, 'delivery_info.html', {
                'delivery_form': form,
                'totals': total
            })

    # GET-запит — просто рендеримо форму
    form = DeliveryForm()

    return redirect(request, 'delivery_info', {
        'delivery_form': form,
        'totals': total
    })


def process_payment(request):
    form = PaymentForm(request.POST)
    if form.is_valid():
        card_date = form.cleaned_data
        #TODO logic to payment
        #TODO make webhook work if and update id payment from paypal if success

