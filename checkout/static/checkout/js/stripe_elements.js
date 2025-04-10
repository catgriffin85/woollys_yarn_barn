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

    // Handle real-time validation errors on the card element
    card.addEventListener('change', function (event) {
        const errorDiv = document.getElementById('card-errors');
        if (event.error) {
            const html = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${event.error.message}</span>
            `;
            $(errorDiv).html(html);
        } else {
            errorDiv.textContent = '';
        }
    });

    const form = document.getElementById('payment-form');

    form.addEventListener('submit', function (ev) {
        ev.preventDefault();
        card.update({ 'disabled': true });
        $('#submit-button').attr('disabled', true);
        $('#payment-form').fadeToggle(100);
        $('#loading-overlay').fadeToggle(100);

        const saveInfo = Boolean($('#id-save-info').attr('checked'));
        const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        const postData = {
            'csrfmiddlewaretoken': csrfToken,
            'client_secret': clientSecret,
            'save_info': saveInfo,
        };
        const url = '/checkout/cache_checkout_data/';

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
            },
            shipping: {
                name: form.full_name.value.trim(),
                phone: form.phone_number.value.trim(),
                address: {
                    line1: form.street_address1.value.trim(),
                    line2: form.street_address2.value.trim(),
                    city: form.town_or_city.value.trim(),
                    country: form.country.value,
                    postal_code: form.postcode.value.trim(),
                    state: form.county.value.trim(),
                }
            }
        }).then(function (result) {
            if (result.error) {
                const errorDiv = document.getElementById('card-errors');
                const html = `
                    <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>
                `;
                $(errorDiv).html(html);
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false });
                $('#submit-button').attr('disabled', false);
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    $.post(url, postData).done(function () {
                        form.submit();
                    }).fail(function () {
                        location.reload();
                    });
                }
            }
        });
    });
});
