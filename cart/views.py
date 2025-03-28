from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages

from stock.models import Stock


def view_cart(request):
    """ A view that renders the cart contents page """
    print("Cart contents:", request.session.get('cart', {}))
    return render(request, 'cart/cart.html')


def add_to_cart(request, item_id):
    """ Add a quantity of the specified stock to the shopping cart, considering weight, colour, or size if applicable """

    cart = request.session.get('cart', {})

    quantity = int(request.POST.get('quantity', 1))
    stock = get_object_or_404(Stock, pk=item_id)
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
        messages.success(request, f'Added {quantity} of {stock.name} to your cart!')

    else:
        if 'items_by_attributes' not in cart[item_id]:
            cart[item_id]['items_by_attributes'] = {}

        if attributes in cart[item_id]['items_by_attributes']:
            cart[item_id]['items_by_attributes'][attributes] += quantity
            messages.success(request, f'Updated quantity of {stock.name} in your cart!')
        else:
            cart[item_id]['items_by_attributes'][attributes] = quantity
            messages.success(request, f'Added {quantity} of {stock.name} to your cart!')
            
    request.session['cart'] = cart
    request.session.modified = True

    return redirect(redirect_url)


def adjust_cart(request, item_id):
    """ Adjust the quantity of the specified stock to the specified amount """

    quantity = int(request.POST.get('quantity'))
    stock = get_object_or_404(Stock, pk=item_id)
    cart = request.session.get('cart', {})

    weight = request.POST.get('stock_weight', None)
    colour = request.POST.get('stock_colour', None)
    size = request.POST.get('stock_size', None)

    # Format the attributes string based on available values
    attributes = f"{size or 'None'}-{weight or 'None'}-{colour or 'None'}"

    if quantity > 0:
        if item_id not in cart:
            cart[item_id] = {
                "stock_id": int(item_id),
                "quantity": quantity,
                "items_by_attributes": {}
            }

        # Update the quantity for the specified attribute (or add it if it doesn't exist)
        if attributes in cart[item_id]["items_by_attributes"]:
            cart[item_id]["items_by_attributes"][attributes] += quantity
        else:
            cart[item_id]["items_by_attributes"][attributes] = quantity

        messages.success(request, f'Updated quantity of {stock.name} in your cart!')

    else:
        # Remove the item if quantity is zero or less
        cart.pop(item_id, None)

    # Save the updated cart to the session
    request.session['cart'] = cart

    return redirect(reverse('view_cart'))


def remove_from_cart(request, item_id):
    """ Remove an item from the cart """
    
    stock = get_object_or_404(Stock, pk=item_id)
    
    try:
        cart = request.session.get('cart', {})

        if item_id in cart:
            cart.pop(item_id)
            messages.success(request, f'{stock.name} removed in your cart!')
        
        request.session['cart'] = cart
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)