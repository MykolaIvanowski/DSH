import json
import requests
import logging
from django.db import transaction

from django.utils import timezone
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
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


logger = logging.getLogger(__name__)


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


def log_order_change(order, *, status=None, status_pay=None,amount_paid=None, note=''):
    OrderLog.objects.create(
        order=order,
        status=status or order.status,
        status_pay=status_pay or order.status_pay,
        amount_paid=amount_paid or order.amount_paid,
        note=note
    )

@csrf_exempt
def paypal_webhook(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        event_type = data.get("event_type")

        if event_type == "CHECKOUT.ORDER.APPROVED":
            order_id = data["resource"]["id"]
            try:
                order = Order.objects.get(paypal_order_id=order_id)
                order.status = 'approved'
                order.save()
                log_order_change(order, note='Webhook: CHECKOUT.ORDER.APPROVED')
            except Order.DoesNotExist:
                logger.warning(f"Webhook: Order {order_id} not found")

        elif event_type == "PAYMENT.CAPTURE.COMPLETED":
            order_id = data["resource"]["supplementary_data"]["related_ids"]["order_id"]
            amount = data["resource"]["amount"]["value"]

            try:
                order = Order.objects.get(paypal_order_id=order_id)
                if order.status_pay != 'paid':
                    order.status_pay = 'paid'
                    order.amount_paid = amount
                    order.save()
                    log_order_change(order, amount_paid=amount, note='Webhook: PAYMENT.CAPTURE.COMPLETED')
            except Order.DoesNotExist:
                logger.warning(f"Webhook: Order {order_id} not found")

        return JsonResponse({"status": "received"})

    except Exception as e:
        logger.exception(f"Webhook error: {e}")
        return JsonResponse({"error": "Webhook processing failed"}, status=500)


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
    if request.user.is_authenticated and request.user.is_superuser:

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
    else:
        raise Http404('Nothing here, resource not found')


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

        if item.quantity > product.stock:
            messages.error(request, f"Not enough stock for {product.name}")
            return redirect('cart')

        product.stock -= item.quantity
        product.save()

    access_token = get_access_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    order_payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "EUR",
                "value": str(order.amount_paid)
            }
        }],
        "application_context": {
            "return_url": request.build_absolute_uri("/payment_success/"),
            "cancel_url": request.build_absolute_uri("/payment_cancel/")
        }
    }

    response = requests.post(
        "https://api-m.sandbox.paypal.com/v2/checkout/orders",
        headers=headers,
        json=order_payload
    )
    data = response.json()

    order.paypal_order_id = data.get("id")
    order.status = 'approved'
    order.save()

    for link in data.get("links", []):
        if link['rel'] == 'approve':
            messages.success(request, 'Redirecting to PayPal...')
            return redirect(link['href'])

    messages.error(request, "Could not create PayPal order")
    return redirect('delivery_info')


@transaction.atomic
def payment_failed(request):
    order = get_order_from_session_or_db(request)
    if order and order.status == 'approved' and order.status_pay == 'pending':
        for item in order.items.all():
            product = Product.objects.select_for_update().get(id=item.product.id)
            product.stock += item.quantity
            product.save()

        order.status = 'canceled'
        order.status_pay = 'rejected'
        order.save()

        messages.warning(request, 'Payment was canceled. Items returned to stock.')
    return render(request, "payment_failed.html", {})


@transaction.atomic
def payment_success(request):
    paypal_order_id = request.GET.get('token')
    if not paypal_order_id:
        messages.error(request, 'Missing PayPal token.')
        return redirect('cart_view')

    try:
        order = Order.objects.get(paypal_order_id=paypal_order_id)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('cart_view')

    if not verify_paypal_capture(order):
        for item in order.items.all():
            product = Product.objects.select_for_update().get(id=item.product.id)
            product.stock += item.quantity
            product.save()

        order.status = 'canceled'
        order.status_pay = 'rejected'
        order.save()

        messages.error(request, 'Payment verification failed. Items returned to stock.')
        return redirect('cart_view')

    access_token = get_access_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    capture_url = f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}/capture'
    response = requests.post(capture_url, headers=headers)
    data = response.json()

    if data.get('status') == 'COMPLETED':
        order.status = 'approved'
        order.status_pay = 'paid'
        order.save()
        messages.success(request, 'Payment completed successfully.')
    else:
        messages.error(request, f"Capture failed: {data.get('status')}")
        return redirect('cart_view')

    return render(request, "payment_success.html", {})


def get_order_from_session_or_db(request):
    order_id = request.session.get('paypal_order_id')
    if order_id:
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            pass
    return None


def verify_paypal_capture(order):
    access_token = get_access_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    url = f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{order.paypal_order_id}'

    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get('status') == 'COMPLETED'
    except Exception as e:
        logger.exception(f'Error: {e}')
        return False

