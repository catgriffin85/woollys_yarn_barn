from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import NewsletterSignupForm
from stock.models import Stock


def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsletterSignupForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data['email']
            print(f"Newsletter signup received from: {email}")

            send_mail(
                'Newsletter Signup Confirmation',
                'Thank you for signing up for our newsletter!',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, 'Thank you for signing up for our newsletter!')
            return redirect('home')
    else:
        form = NewsletterSignupForm()

    return render(request, 'newsletter/signup.html', {'form': form})

