from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

from .models import Order, OrderLineItem
from stock.models import Stock
from .forms import OrderForm
from cart.contexts import cart_contents

import stripe


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
    )

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.order_total = total
            order.delivery_cost = 0
            order.grand_total = total
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
                stock_id = item_data.get('stock_id')
                quantity = item_data.get('quantity', 1)
                if stock_id:
                    try:
                        stock = Stock.objects.get(id=stock_id)
                        line_item = OrderLineItem.objects.create(
                            order=order,
                            stock=stock,
                            quantity=quantity
                        )
                        print(f"Created line item: {line_item}")
                    except Stock.DoesNotExist:
                        print(f"No Stock ID {stock_id} not found.")
                        continue

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

    print("Cart contents:", cart)
    print("Form valid:", order_form.is_valid())

    return render(request, 'checkout/checkout.html', context)


def order_complete(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    context = {
        'order': order,
    }

    return render(request, 'checkout/order_complete.html', context)
