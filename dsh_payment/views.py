import json
import requests
from django.db import transaction

from django.utils import timezone
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from requests.auth import HTTPBasicAuth

from app_dsh.models import Product
from dsh.settings import CLIENT_ID, CLIENT_SECRET
from dsh_payment.forms import DeliveryForm
from dsh_payment.models import Order, OrderItem, OrderLog, STATUS_CHOICES
from cart.cart import Cart
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator



#TODO could be  with payment form on payment view
def checkout(request):
    cart = Cart(request)
    delivery_form = DeliveryForm(request.POST or None)
    return render(request, "checkout.html",
                  {"cart_products":cart.get_products(), "cart_quantities": cart.get_quantities(),
                   "totals":cart.cart_total_products(), "delivering_form":delivery_form})


def get_access_token_mock():
    return "mock_token"


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


def confirm_order_view(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    # check availability for products
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

    # logining
    OrderLog.objects.create(order=order, status='delivered', note='Order confirmed')

    messages.success(request, "Order confirmed and stock updated")
    return redirect('order_list')


@require_http_methods(["GET", "POST"])
def order_dashboard_view(request):
    if not (request.user.is_authenticated and request.user.is_superuser):
        raise Http404('Nothing here, resource not found')

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")

        if order_id and new_status:
            order = get_object_or_404(Order, pk=order_id)
            if new_status in dict(STATUS_CHOICES):
                order.status = new_status
                order.save()
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
        raise Http404('Nothing here resource not found')



def order_item_view(request, item_id):
    if request.user.is_authenticated and request.user.is_superuser:
        order = get_object_or_404(Order, id=item_id)
        items = OrderItem.objects.filter(order=order).select_related('product')
        oreder_totals = sum(item.quantity * item.price for item in items )
        return render(request, 'order_items.html', {
            'order': order,
            'items': items,
            'order_totals':oreder_totals,
        })
    else:
        raise Http404('Nothing here, resource not found')


def delivery_info_view(request):
    cart = Cart(request)
    cart_products = cart.get_products()
    quantity = cart.get_quantities()
    total = cart.cart_total_products()
    if total == 0:
        messages.error(request, "Your cart is empty. Please add item before order")
        return redirect('home')
    if request.method == 'POST':

        form = DeliveryForm(request.POST)
        action = request.POST.get("action")

        if form.is_valid():
            order = form.save(commit=False)
            order.status = 'created'
            order.amount_paid = 0 if action == "pay_later" else total
            order.save()

            # save order position
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

            # clear session
            request.session.pop('session_key', None)

            if action == "pay_later":
                return redirect('order_success')

            elif action == "pay_online":
                return redirect('payment_view', order_id=order.id)

        else:
            messages.error(request, 'Form is not valid.')
            return render(request, 'delivery_info.html', {
                'delivery_form': form,
                'totals': total
            })

    # GET render form
    form = DeliveryForm()

    return render(request, 'delivery_info.html', {
        'delivery_form': form,
        'totals': total
    })

def order_success_view(request):
    return render(request, 'order_success.html')


@transaction.atomic
def payment_paypal_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    for item in order.items.all():
        product = Product.objects.select_for_update().get(id=item.product.id)
        if product.stock < item.quantity and not product.allow_backorder:
            messages.error(request, 'Not enough stock')
            return redirect('cart')
        product.stock -= item.quantity
        product.save()
    access_token = get_access_token()

    headers = {
        'Content-Type': 'application/json',
        'Authorization' : f'Bearer {access_token}'
    }

    order_payload = {
        "intent" : "CAPTURE",
        "purchase_units":[{
            "amount": {
                "currency_code": "EUR",
                "value" : str(order.amount_paid)
            }
        }],
        "application_content": {
            "return_url": request.build_absolute_uri("/payment_success/"),
            "cancel_url": request.build_absolute_uri("/payment_cancel/")
        }
    }
    responce = requests.post("https://api-m.sandbox.paypal.com/v2/checkout/orders",
                            headers=headers, json=order_payload )
    data = responce.json()
    for link in data.get("links", []):
        if link['rel'] == 'approve':
            messages.success(request, 'Redirect to Paypal')
            return redirect(link['href'])

    messages.error(request, "Could not create Paypal order")
    return redirect('delivery_info')


@transaction.atomic
def payment_failed(request):
    order = get_order_from_session_or_db(request)
    if order.status == 'pending':
        for item in order.items.all():
            product = Product.objects.select_for_update().get(id=item.product.id)
            product.stock += item.quantity
            product.save()
        order.status = 'failed'
        order.save()
        messages.warning(request, 'Payment was canceled. item return to stock')
    return render(request,"payment_failed.html", {})


def payment_success(request):
    order = get_order_from_session_or_db(request)
    if not verify_paypal_capture(order):
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()
        messages.error(request,'Payment failed')
        return redirect('cart_view')
    order_id =  request.GET.get('token')
    access_token = get_access_token()
    response = requests.post(f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture',
                            headers = {'Content-Type':'application/json', 'Authorization':f'Bearer {access_token}'})
    data = response.json()
    if data.get('status') == 'COMPLETE':
        order.status = 'paid'
        order.save()
        messages.success(request, 'Payment completed successfully')
    else:
        messages.error(request, f'Capture failed: {data.get('status')}')
    return render(request, "payment_success.html",{})


def get_order_from_session_or_db(request):
    order_id = request.session.get('paypal_order_id')
    if order_id:
        try:
            return Order.objects.get(id=order_id)
        except:
            pass


def verify_paypal_capture(order):
    access_token = get_access_token()

    headers = {
        'Content-Type':'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    paypal_order_id = order.paypal_order_id

    url = f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}'

    try :
        response = requests.get(url, headers= headers)
        data = response.json()
        return data.get('status') == 'COMPLETED'
    except Exception as e :

        return False


