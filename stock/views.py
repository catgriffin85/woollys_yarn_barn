from django.shortcuts import render, get_object_or_404
from .models import Stock


def shop_all(request):
    """ A view to show all stock on the site, including sorting and searching """

    stocks = Stock.objects.all()

    context = {
        'stocks': stocks,
    }

    return render(request, 'stock/stock.html', context)


def stock_detail(request, stock_id):
    """ A view to show individual stock details """

    stock = get_object_or_404(Stock, pk=stock_id)

    context = {
        'stock': stock,
    }

    return render(request, 'stock/stock_detail.html', context)