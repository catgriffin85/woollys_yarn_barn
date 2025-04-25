from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

from .models import Faq

from .forms import ContactForm


def all_faqs(request):
    """ A view to show all faqs """

    faqs = Faq.objects.all()
    topics = None

    if request.GET:

        if 'topics' in request.GET:
            topics = request.GET['topic'].split(',')
            faqs = faqs.filter(topic__name__in=topics)
            topics = Faq.objects.filter(name__in=faqs)

    context = {
        'faqs': faqs,
        'current_topics': topics,
    }

    return render(request, 'customer_service/faqs.html', context)


def faq_view(request):
    """
    Display FAQs grouped by predefined topics.
    """
    faqs_delivery = Faq.objects.filter(topics="delivery", is_published=True)
    faqs_returns_refunds = Faq.objects.filter(
        topics="returns_refunds", is_published=True
    )
    faqs_order_issues = Faq.objects.filter(
        topics="order_issues", is_published=True
    )
    faqs_stock = Faq.objects.filter(topics="stock", is_published=True)
    faqs_payment_queries = Faq.objects.filter(
        topics="payment_queries", is_published=True
    )

    context = {
        'faqs_delivery': faqs_delivery,
        'faqs_returns_refunds': faqs_returns_refunds,
        'faqs_order_issues': faqs_order_issues,
        'faqs_stock': faqs_stock,
        'faqs_payment_queries': faqs_payment_queries,
    }
    return render(request, "customer_service/faqs.html", context)


def contact(request):
    """
    Handle the contact form view.
    """
    selected_topic = request.POST.get('topic') or request.GET.get('topic')

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)

        if 'customer_question' in request.POST and contact_form.is_valid():
            contact_form.save()
            # Send confirmation email
            user_email = contact_form.cleaned_data.get('email')
            user_name = contact_form.cleaned_data.get('full_name')
            subject = 'Your Query Has Been Received'
            message = (
                f"Hi {user_name},\n\n"
                "Thank you for getting in touch with us. "
                "We will respond as soon as possible.\n\n"
                "Best regards,\nThe Support Team"
            )

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=False,
            )

            messages.success(
                request,
                "We have received your query."
                "Our Customer Service Team will be in touch shortly!"
            )
            return redirect('home')

    else:
        contact_form = ContactForm(initial={'topic': selected_topic})

    if request.method == 'POST' and not contact_form.is_valid():
        contact_form = ContactForm(request.POST)

    faqs = (
        Faq.objects.filter(topics=selected_topic, is_published=True)
        if selected_topic else None
    )

    context = {
        'contact_form': contact_form,
        'faqs': faqs,
        'selected_topic': selected_topic,
        'topic_choices': contact_form.fields['topic'].choices,
    }

    return render(request, 'customer_service/customer_service.html', context)


@csrf_exempt
def contact_thank_you(request):
    """
    Respond to a thank-you action after interacting with FAQs.
    """
    if request.method == 'POST':
        messages.success(request, "Great! We're glad we could help. 😊")
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


def home(request):
    """
    Display the homepage, showing a thank-you message if redirected from FAQ/contact.
    """
    if request.GET.get('thank_you') == '1':
        messages.success(request, "Great! We're glad we could help. 😊")

    return render(request, 'home/index.html')
