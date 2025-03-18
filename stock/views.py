from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Stock


def shop_all(request):
    """ A view to show all stock on the site, including sorting and searching """

    stocks = Stock.objects.all()
    query = None

    if request.GET:
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria")
                return redirect(reverse('stock'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            stocks = stocks.filter(queries)

    context = {
        'stocks': stocks,
        'search_term': query,
    }

    return render(request, 'stock/stock.html', context)


def stock_detail(request, stock_id):
    """ A view to show individual stock details """

    stock = get_object_or_404(Stock, pk=stock_id)

    context = {
        'stock': stock,
    }

    return render(request, 'stock/stock_detail.html', context)