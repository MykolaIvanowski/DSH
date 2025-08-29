from datetime import datetime

from django.shortcuts import render,redirect
from dsh_payment.models import Order, OrderItem
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

def not_shipped_dash(request):
    pass
def shipped_dash(request):
    pass
def process_order(request):
    pass
def billing_info(request):
    pass
def checkout(request):
    pass
def payment_failed(request):
    pass
def payment_success(request):
    pass