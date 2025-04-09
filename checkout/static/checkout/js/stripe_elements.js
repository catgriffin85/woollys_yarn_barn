/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

document.addEventListener("DOMContentLoaded", function () {
    const stripePublicKey = JSON.parse(
        document.getElementById('id_stripe_public_key').textContent
    );
    const clientSecret = JSON.parse(
        document.getElementById('id_client_secret').textContent
    );

    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();
    
    const style = {
        base: {
            color: '#000',
            fontFamily: '"Quicksand", sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': {
                color: '#aab7c4',
            }
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545'
        }
    };

    const card = elements.create('card', { style: style });
    card.mount('#card-element');

    card.on('change', function (event) {
        const errorDiv = document.getElementById('card-errors');
        if (event.error) {
            errorDiv.textContent = event.error.message;
        } else {
            errorDiv.textContent = '';
        }
    });

    const form = document.getElementById('payment-form');
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: form.full_name.value.trim(),
                    email: form.email.value.trim(),
                    phone: form.phone_number.value.trim(),
                    address: {
                        line1: form.street_address1.value.trim(),
                        line2: form.street_address2.value.trim(),
                        city: form.town_or_city.value.trim(),
                        country: form.country.value,
                        state: form.county.value.trim(),
                        postal_code: form.postcode.value.trim()
                    }
                }
            }
        }).then(function (result) {
            if (result.error) {
                const errorDiv = document.getElementById('card-errors');
                errorDiv.textContent = result.error.message;
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    });
});