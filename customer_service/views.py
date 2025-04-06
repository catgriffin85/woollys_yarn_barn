from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.db.models import Q

from .models import Faq

from .forms import ContactForm


def all_faqs(request):
    """ A view to show all faqs """

    faqs = Faq.objects.all()
    query = None
    topics = None

    if request.GET:

        if 'topics' in request.GET:
            topics = request.GET['topic'].split(',')
            faqs = faqs.filter(topic__name__in=topics)
            topics = Faq.objects.filter(name__in=faqs)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('faqs'))
                
            queries = Q(question__icontains=query) | Q(description__icontains=query)
            faqs = faqs.filter(queries)

    context = {
        'faqs': faqs,
        'search_term': query,
        'current_topics': topics,
    }

    return render(request, 'customer_service/faqs.html', context)


def faq_view(request):
    faqs_delivery = Faq.objects.filter(topics="delivery", is_published=True)
    faqs_returns_refunds = Faq.objects.filter(topics="returns_refunds", is_published=True)
    faqs_order_issues = Faq.objects.filter(topics="order_issues", is_published=True)
    faqs_stock = Faq.objects.filter(topics="stock", is_published=True)
    faqs_payment_queries = Faq.objects.filter(topics="payment_queries", is_published=True)

    context = {
        'faqs_delivery': faqs_delivery,
        'faqs_returns_refunds': faqs_returns_refunds,
        'faqs_order_issues': faqs_order_issues,
        'faqs_stock': faqs_stock,
        'faqs_payment_queries': faqs_payment_queries,
    }
    return render(request, "customer_service/faqs.html", context)


def contact(request):
    selected_topic = request.GET.get('topic')
    contact_form = ContactForm(initial={'topic': selected_topic})
    faqs = None

    if selected_topic:
        faqs = Faq.objects.filter(topics=selected_topic)

    context = {
        'contact_form': contact_form,
        'faqs': faqs,
    }
    return render(request, 'customer_service/customer_service.html', context)
