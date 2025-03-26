from django.shortcuts import render, redirect, reverse, HttpResponse


def view_cart(request):
    """ A view that renders the cart contents page """

    return render(request, 'cart/cart.html')


def add_to_cart(request, item_id):
    """ Add a quantity of the specified stock to the shopping cart, considering weight, colour, or size if applicable """

    cart = request.session.get('cart', {})

    quantity = int(request.POST.get('quantity', 1))

    redirect_url = request.POST.get('redirect_url', '/')

    weight = request.POST.get('stock_weight', None)
    colour = request.POST.get('stock_colour', None)
    size = request.POST.get('stock_size', None)

    attributes = f"{size or 'None'}-{weight or 'None'}-{colour or 'None'}"

    if item_id not in cart:
        cart[item_id] = {
                    "stock_id": int(item_id),
                    "quantity": quantity,
                    "items_by_attributes": {attributes: quantity}
                }
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


def adjust_cart(request, item_id):
    """ Adjust the quantity of the specified stock to the specified amount """

    quantity = int(request.POST.get('quantity'))
    
    cart = request.session.get('cart', {})

    if quantity > 0:
            cart[item_id] = quantity
    else:
            cart.pop(item_id)

    request.session['cart'] = cart
    return redirect(reverse('view_cart'))


def remove_from_cart(request, item_id):
    """ Remove an item from the cart """
    try:
        cart = request.session.get('cart', {})

        if item_id in cart:
            cart.pop(item_id)
        
        request.session['cart'] = cart
        return HttpResponse(status=200)

    except Exception:
        return HttpResponse(status=500)
