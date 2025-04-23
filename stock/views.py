from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Stock, Category
from .forms import StockForm


def shop_all(request):
    """ A view to show all stock, including sorting and search queries """

    stocks = Stock.objects.all()
    query = None
    categories = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']

            if sortkey == 'reset':
                return redirect(reverse('stock'))

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
                messages.error(
                    request,
                    "You didn't enter any search criteria!"
                )
                return redirect(reverse('stock'))

            queries = (
                Q(name__icontains=query) | Q(description__icontains=query)
            )
            stocks = stocks.filter(queries)

    current_sorting = (
        f"{request.GET.get('sort', 'None')}_{request.GET.get('direction', 'None')}"
    )

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


def add_stock(request):
    """"Add a stock to the store"""
    if request.method == 'POST':
        form = StockForm(request.POST, request.FILES)
        if form.is_valid():
            stock = form.save()
            messages.success(request, 'Successfully added new stock!')
            return redirect(reverse('stock_detail', args=[stock.id]))
        else:
            messages.error(
                request,
                'Failed to add any stock. Please ensure the form is valid.'
            )
    else:
        form = StockForm()

    template = 'stock/add_stock.html'
    context = {
        'form': form
    }

    return render(request, template, context)


def edit_stock(request, stock_id):
    """ Edit a stock in the store """
    stock = get_object_or_404(Stock, pk=stock_id)
    if request.method == 'POST':
        form = StockForm(request.POST, request.FILES, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated your stock!')
            return redirect(reverse('stock_detail', args=[stock.id]))
        else:
            messages.error(
                request,
                'Failed to update your stock. Please ensure the form is valid.'
            )
    else:
        form = StockForm(instance=stock)

        if not stock.weight:
            form.fields.pop('weight')
        if not stock.colour:
            form.fields.pop('colour')
        if not stock.size:
            form.fields.pop('size')

        messages.info(request, f'You are editing {stock.name}')

    template = 'stock/edit_stock.html'
    context = {
        'form': form,
        'stock': stock,
    }

    return render(request, template, context)


def delete_stock(request, stock_id):
    """ Confirm and delete a stock from the store """
    stock = get_object_or_404(Stock, pk=stock_id)

    if request.method == 'POST':
        stock.delete()
        messages.success(request, 'Stock deleted!')
        return redirect(reverse('stock'))

    return render(request, 'stock/stock.html', {'stock': stock})
