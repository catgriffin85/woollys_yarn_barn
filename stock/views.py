from django.shortcuts import render
from .models import Stock


def shop_all(request):
    """ A view to show all stock on the site, including sorting and searching """

    stock = Stock.objects.all()

    context = {
        'stock': stock,
    }

    return render(request, 'stock/stock.html', context)