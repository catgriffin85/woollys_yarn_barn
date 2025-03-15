from django.shortcuts import render
from .models import Stock


def shop_all(request):
    """ A view to show all stock on the site, including sorting and searching """

    stocks = Stock.objects.all()

    context = {
        'stocks': stocks,
    }

    return render(request, 'stock/stock.html', context)