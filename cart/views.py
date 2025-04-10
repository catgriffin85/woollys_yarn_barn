from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages
from cart.utils import format_cart_attributes

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

    attributes = format_cart_attributes(size, weight, colour)

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
    """ Adjust the quantity of a specific attribute combination in the cart """

    item_id = str(item_id)  # Ensure item_id is a string for session storage
    quantity = request.POST.get('quantity', '0')  # Default to '0' if missing

    try:
        quantity = int(quantity)
    except ValueError:
        messages.error(request, "Invalid quantity value.")
        return redirect(reverse('view_cart'))

    stock = get_object_or_404(Stock, pk=item_id)
    cart = request.session.get('cart', {})

    # Extract attribute values from POST
    weight = request.POST.get('stock_weight', None)
    colour = request.POST.get('stock_colour', None)
    size = request.POST.get('stock_size', None)

    # Format attributes into a consistent key
    attributes = format_cart_attributes(size, weight, colour)
    print("Adjusting attributes:", attributes)

    if item_id not in cart or not isinstance(cart[item_id], dict):
        messages.warning(request, "Item not found in cart.")
        return redirect(reverse('view_cart'))

    if 'items_by_attributes' not in cart[item_id]:
        cart[item_id]['items_by_attributes'] = {}

    if quantity > 0:
        cart[item_id]['items_by_attributes'][attributes] = quantity
        cart[item_id]['quantity'] = sum(cart[item_id]['items_by_attributes'].values())
        messages.success(request, f"Updated quantity of {stock.name} ({attributes}) to {quantity}.")
    else:
        if attributes in cart[item_id]['items_by_attributes']:
            del cart[item_id]['items_by_attributes'][attributes]

            # Recalculate total quantity
            total_quantity = sum(cart[item_id]['items_by_attributes'].values())

            if total_quantity > 0:
                cart[item_id]['quantity'] = total_quantity
            else:
                del cart[item_id]  # Remove the whole item if no attributes left

            messages.success(request, f"Removed {stock.name} ({attributes}) from your cart.")
        else:
            messages.warning(request, "Attribute combination not found in cart.")

    request.session['cart'] = cart
    return redirect(reverse('view_cart'))


def remove_from_cart(request, item_id):
    """ Remove a specific attribute combination of an item from the cart """

    stock = get_object_or_404(Stock, pk=item_id)

    try:
        cart = request.session.get('cart', {})

        item_id = str(item_id)
        weight = request.POST.get('stock_weight', None)
        colour = request.POST.get('stock_colour', None)
        size = request.POST.get('stock_size', None)

        attributes = format_cart_attributes(size, weight, colour)
        print("Looking for attributes:", attributes)
        print("Available keys:", cart[item_id]['items_by_attributes'].keys())
        
        if item_id in cart and 'items_by_attributes' in cart[item_id]:
            if attributes in cart[item_id]['items_by_attributes']:
                del cart[item_id]['items_by_attributes'][attributes]

                # Recalculate total quantity
                total_quantity = sum(cart[item_id]['items_by_attributes'].values())

                if total_quantity > 0:
                    cart[item_id]['quantity'] = total_quantity
                else:
                    del cart[item_id]  # No variants left, remove the whole item

                messages.success(request, f'Removed {stock.name} ({attributes}) from your cart!')
            else:
                messages.warning(request, f'Item with specified attributes not found in cart.')
        else:
            messages.warning(request, f'Item not found in cart.')

        request.session['cart'] = cart
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)