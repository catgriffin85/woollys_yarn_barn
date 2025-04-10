from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

from .models import Order, OrderLineItem
from stock.models import Stock
from .forms import OrderForm
from cart.contexts import cart_contents

import stripe
import json


@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'cart': json.dumps(request.session.get('cart', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('stock')

    current_cart = cart_contents(request)
    total = current_cart['grand_total']
    stripe_total = round(total * 100)

    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
        metadata={
            'cart': json.dumps(cart),
            'username': request.user.username if request.user.is_authenticated else 'anonymous',
        },
    )

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_cart = json.dumps(cart)
            order.save()

            # Send confirmation email
            user_email = order_form.cleaned_data.get('email')
            user_name = order_form.cleaned_data.get('full_name')
            subject = 'Your Order Has Been Received'
            message = (
                f"Hi {user_name},\n\n"
                "Thank you for your order.\n\n"
                "Best regards,\nWoolly's Yarn Barn Team"
            )

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=False,
            )

            for item_id, item_data in cart.items():
                try:
                    stock = Stock.objects.get(id=item_data['stock_id'])
                    attributes = item_data.get('items_by_attributes', {})

                    for attr_key, quantity in attributes.items():
                        stock_size, stock_weight, stock_colour = attr_key.split('-')

                        order_line_item = OrderLineItem(
                            order=order,
                            stock=stock,
                            quantity=quantity,
                            stock_size=stock_size if stock_size != "None" else None,
                            stock_weight=stock_weight if stock_weight != "None" else None,
                            stock_colour=stock_colour if stock_colour != "None" else None,
                        )
                        order_line_item.save()

                except Stock.DoesNotExist:
                    messages.error(request, "One of the items in your cart is no longer available.")
                    order.delete()
                    return redirect('view_cart')

                order.update_total()
            # Clear the cart
            request.session['cart'] = {}

            return redirect('order_complete', order_number=order.order_number)
        else:
            messages.error(request, "Form error. Please try again.")
    else:
        order_form = OrderForm()

    context = {
        'order_form': order_form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': intent.client_secret,
    }

    return render(request, 'checkout/checkout.html', context)


def order_complete(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    context = {
        'order': order,
    }

    return render(request, 'checkout/order_complete.html', context)
