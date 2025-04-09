from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .models import Order, OrderLineItem
from .forms import OrderForm
from cart.contexts import cart_contents

import stripe

def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Your cart is empty")
        return redirect(reverse('stock'))

    current_cart = cart_contents(request)
    total = current_cart['grand_total']
    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            # You can add more order fields here if needed
            order.save()

            # Clear the cart from session
            request.session['cart'] = {}

            messages.success(request, 'Your order has been received!')

            return render(request, 'checkout/order_complete.html')
        else:
            messages.error(request, 'There was an error with your form. Please double-check your information.')
    else:
        order_form = OrderForm()
    
    if request.method == 'POST' and order_form.is_valid():
        order = order_form.save(commit=False)
        order.order_total = total
        order.grand_total = total
        order.save()

        for item in cart.values():
            stock = item['stock']
            quantity = item['quantity']
            OrderLineItem.objects.create(
                order=order,
                stock=stock,
                quantity=quantity,
                lineitem_total=product.price * quantity
            )
        
        return redirect('order_complete', order_number=order.order_number)

    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, 'checkout/checkout.html', context)

def order_complete(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    
    context = {
        'order': order,
    }
    return render(request, 'checkout/order_complete.html', context)
