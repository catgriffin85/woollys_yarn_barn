from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from cart.contexts import cart_contents

import stripe
import json


@require_POST
def cache_checkout_data(request):
    """
    Store cart and user data in the metadata of the Stripe PaymentIntent.

    This helps ensure that relevant information can be accessed from Stripe
    in the event of payment issues or review.
    """
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
        messages.error(
            request,
            'Sorry, your payment cannot be processed. Please try again later.'
        )
        return HttpResponse(content=e, status=400)


def checkout(request):
    """
    Display and handle the checkout form, integrating with Stripe for payment.
    """

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
            'username': (
                request.user.username
                if request.user.is_authenticated else 'anonymous'
            ),
        },
    )

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            pid = request.POST.get('client_secret').split('_secret')[0]
            pid = pid.split('_secret')[0]

            save_info = 'save_info' in request.POST
            request.session['save_info'] = save_info
            request.session['cart'] = {}

            return redirect('order_complete', stripe_pid=pid)

        else:
            messages.error(request, "Form error. Please try again.")
    else:
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'town_or_city': profile.default_town_or_city,
                    'county': profile.default_county,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

    context = {
        'order_form': order_form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': intent.client_secret,
    }

    return render(request, 'checkout/checkout.html', context)


def order_complete(request, stripe_pid):
    """
    Handle the order completion logic after payment.
    """
    save_info = request.session.get('save_info')
    order = Order.objects.filter(stripe_pid=stripe_pid).first()

    if not order:
        messages.info(
            request,
            "Your order is being processed. Refresh this page for update."
        )
        return render(
            request,
            'checkout/order_complete_pending.html', {'stripe_pid': stripe_pid}
        )

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

        if save_info:
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_town_or_city': order.town_or_city,
                'default_county': order.county,
                'default_country': order.country,
                'default_postcode': order.postcode,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    return render(request, 'checkout/order_complete.html', {'order': order})
