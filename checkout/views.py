from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty")
        return redirect(reverse('products'))
    
    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51QpEhMAuYHlxCm28Sv8ZnsIPMA9742ih5b497aCQCjf0WezZ2wIw2T7wOPZw4obWEHIusd9XBUbyPWHM0rQopJwC00tdkJQqZ8',
        'client_secret':'test',
    }

    return render(request, template, context)