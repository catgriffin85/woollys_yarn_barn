from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Stock, Category


def shop_all(request):
    """ A view to show all products, including sorting and search queries """

    stocks = Stock.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']

            if sortkey == 'reset':
                return redirect(reverse('stock'))
    
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                stocks = stocks.annotate(lower_name=Lower('name'))

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            stocks = stocks.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            stocks = stocks.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
                
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            stocks = stocks.filter(queries)

    current_sorting = f"{request.GET.get('sort', 'None')}_{request.GET.get('direction', 'None')}"

    context = {
        'stocks': stocks,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'stock/stock.html', context)



def stock_detail(request, stock_id):
    """ A view to show individual stock details """

    stock = get_object_or_404(Stock, pk=stock_id)

    context = {
        'stock': stock,
    }

    return render(request, 'stock/stock_detail.html', context)