from django.shortcuts import render, redirect
from django.http import HttpResponse

def view_cart(request):
    """ A view that renders the cart contents page """
    return render(request, 'cart/cart.html')

def add_to_cart(request, item_id):
    """ Add a quantity of the specified product to the shopping cart, considering weight, colour, or size if applicable """

    cart = request.session.get('cart', {})

    quantity = int(request.POST.get('quantity', 1))

    redirect_url = request.POST.get('redirect_url', '/')

    weight = request.POST.get('stock_weight', None)
    colour = request.POST.get('stock_colour', None)
    size = request.POST.get('stock_size', None)

    attributes = f"{size or 'None'}-{weight or 'None'}-{colour or 'None'}"

    if item_id not in cart:
        cart[item_id] = {'items_by_attributes': {attributes: quantity}}
    else:
        if 'items_by_attributes' not in cart[item_id]:
            cart[item_id]['items_by_attributes'] = {}

        if attributes in cart[item_id]['items_by_attributes']:
            cart[item_id]['items_by_attributes'][attributes] += quantity
        else:
            cart[item_id]['items_by_attributes'][attributes] = quantity

    request.session['cart'] = cart
    request.session.modified = True

    return redirect(redirect_url)
