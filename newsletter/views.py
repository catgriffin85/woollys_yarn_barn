from django.utils.timezone import now
from .models import NewsletterSignup
from .forms import NewsletterSignupForm, NewsletterUnsubscribeForm
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings


def newsletter_signup(request):
    """
    Handle newsletter signup and resubscription.
    """
    if request.method == 'POST':
        form = NewsletterSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                signup = NewsletterSignup.objects.get(email=email)
                if signup.unsubscribed:
                    # Resubscribe user
                    signup.unsubscribed = False
                    signup.date_unsubscribed = None
                    signup.date_subscribed = now()
                    signup.save()
                    messages.success(
                        request,
                        "Welcome back!n\n"
                        "You have been resubscribed to our newsletter."
                    )
                else:
                    messages.info(request, 'This email is already subscribed.')
                    return redirect('home')
            except NewsletterSignup.DoesNotExist:
                # Brand new signup
                signup = form.save(commit=False)
                signup.date_subscribed = now()
                signup.save()
                messages.success(
                    request,
                    'Thank you for signing up for our newsletter!'
                )

            # Send confirmation email
            subject = 'Newsletter Signup Confirmation'
            message = (
                "Hi there,\n\n"
                "Thank you for signing up for our newsletter!\n\n"
                "We’ll be sending you updates, offers, "
                "and all things yarn.\n\n"
                "If you ever wish to unsubscribe, "
                "you can do so on our website\n\n"
                "Best regards,\nWoolly's Yarn Barn Team"
            )

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return redirect('home')
    else:
        form = NewsletterSignupForm()

    return render(request, 'newsletter/signup.html', {'form': form})


def newsletter_unsubscribe(request):
    """
    Handle newsletter unsubscription.
    """
    if request.method == 'POST':
        form = NewsletterUnsubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                signup = NewsletterSignup.objects.get(email=email)
                if not signup.unsubscribed:
                    signup.unsubscribed = True
                    signup.date_unsubscribed = now()
                    signup.save()
                    messages.success(
                        request,
                        'You have successfully unsubscribed.'
                    )

                    subject = 'You Have Unsubscribed from Our Newsletter'
                    message = (
                        "Hi there,\n\n"
                        "We're sorry to see you go!"
                        "You’ve been unsubscribed from our newsletter.\n\n"
                        "If this was a mistake or you change your mind, "
                        "you can resubscribe anytime on our website.\n\n"
                        "Best wishes,\nWoolly's Yarn Barn Team"
                    )

                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )

                else:
                    messages.info(request, 'You are already unsubscribed.')
            except NewsletterSignup.DoesNotExist:
                messages.error(request, 'This email is not subscribed.')
            return redirect('home')
    else:
        form = NewsletterUnsubscribeForm()

    return render(request, 'newsletter/unsubscribe.html', {'form': form})
