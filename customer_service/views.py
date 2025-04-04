from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.db.models import Q


from .models import Faq, Topic


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

    return render(request, 'customer_service/customer_service.html', context)
