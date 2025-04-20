from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import Order, OrderLineItem
from stock.models import Stock
from .forms import OrderForm
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
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
        messages.error(request, 'Sorry, your payment cannot be processed right now. Please try again later.')
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
                    messages.error(request, "An item in your cart is no longer available.")
                    order.delete()
                    return redirect('view_cart')

                order.update_total()

            save_info = 'save_info' in request.POST
            request.session['save_info'] = save_info

            request.session['cart'] = {}
            return redirect('order_complete', order_number=order.order_number)
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


def order_complete(request, order_number):
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

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

    if not order.email_sent:
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt', {'order': order}).strip()
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt', {
                'order': order,
                'contact_email': settings.DEFAULT_FROM_EMAIL,
            }).strip()

        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [order.email])
        order.email_sent = True
        order.save()

    return render(request, 'checkout/order_complete.html', {'order': order})
