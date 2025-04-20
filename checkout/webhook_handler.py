from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User

from .models import Order, OrderLineItem
from stock.models import Stock
from profiles.models import UserProfile


import json
import time
import stripe


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        subject = render_to_string('checkout/confirmation_emails/confirmation_email_subject.txt', {'order': order}).strip()
        body = render_to_string('checkout/confirmation_emails/confirmation_email_body.txt', {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL}).strip()
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )  

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)
    
    def handle_payment_intent_succeeded(self, event):
        intent = event.data.object
        pid = intent.id
        cart = intent.metadata.get('cart', '{}')
        save_info = intent.metadata.get('save_info', 'false')

        try:
            stripe_charge = stripe.Charge.retrieve(intent.latest_charge)
            billing_details = stripe_charge.billing_details
            shipping_details = intent.shipping or {}
            grand_total = round(stripe_charge.amount / 100, 2)
        except Exception as e:
            return HttpResponse(
                content=f'Webhook error: {e}',
                status=500
            )

        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        profile = None
        username = intent.metadata.username
        if username != 'AnonymousUser':
            try:
                user = User.objects.get(username=username)
                profile = UserProfile.objects.get(user=user)
                if save_info:
                    profile.default_phone_number = shipping_details.phone
                    profile.default_country = shipping_details.address.country
                    profile.default_postcode = shipping_details.address.postal_code
                    profile.default_town_or_city = shipping_details.address.city
                    profile.default_street_address1 = shipping_details.address.line1
                    profile.default_street_address2 = shipping_details.address.line2
                    profile.default_county = shipping_details.address.state
                    profile.save()
            except User.DoesNotExist:
                profile = None

        order_exists = False
        order = None
        attempt = 1

        while attempt <= 5:
            try:
                order = Order.objects.get(stripe_pid=pid)
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        
        if order_exists:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Order already exists',
                status=200
            )

        try:
            order = Order.objects.create(
                full_name=shipping_details.name,
                user_profile=profile,
                email=billing_details.email,
                phone_number=shipping_details.phone,
                country=shipping_details.address.country,
                postcode=shipping_details.address.postal_code,
                town_or_city=shipping_details.address.city,
                street_address1=shipping_details.address.line1,
                street_address2=shipping_details.address.line2,
                county=shipping_details.address.state,
                grand_total=grand_total,
                original_cart=cart,
                stripe_pid=pid,
            )
            for item_id, item_data in json.loads(cart).items():
                stock = Stock.objects.get(id=item_id)
                items = item_data.get("items_by_attributes", {})
                for attribute_key, quantity in items.items():
                    size, weight, colour = attribute_key.split("-")
                    OrderLineItem.objects.create(
                        order=order,
                        stock=stock,
                        quantity=quantity,
                        stock_size=size if size != "None" else None,
                        stock_weight=weight if weight != "None" else None,
                        stock_colour=colour if colour != "None" else None,
                    )
        except Exception as e:
            if order:
                order.delete()
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=500)

        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
