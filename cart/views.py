from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest

from stock.models import Stock


def view_cart(request):
    """ A view that renders the cart contents page """
    print("Cart contents:", request.session.get('cart', {}))
    
    return render(request, 'cart/cart.html')


def add_to_cart(request, item_id):
    """
    Add a quantity of the specified stock to the shopping cart,
    considering weight, colour, or size if applicable.
    """

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
    print("Cart after update:", cart)

    return redirect(redirect_url)


def adjust_cart(request, item_id):
    """ Adjust the quantity of the specified stock item in the cart """

    if item_id == 'undefined' or not item_id.isdigit():
        return HttpResponseBadRequest("Invalid item ID provided.")
    
    item_id = str(item_id)
    quantity = request.POST.get('quantity', '0')

    try:
        quantity = int(quantity)
    except ValueError:
        messages.error(request, "Invalid quantity value.")
        return redirect(reverse('view_cart'))

    stock = get_object_or_404(Stock, pk=item_id)
    cart = request.session.get('cart', {})

    attributes = request.POST.get('item_attribute', 'None-None-None')

    if item_id not in cart:
        cart[item_id] = {
            "stock_id": int(item_id),
            "items_by_attributes": {}
        }

    if quantity > 0:
        cart[item_id]["items_by_attributes"][attributes] = quantity
        cart[item_id]["quantity"] = sum(cart[item_id]["items_by_attributes"].values())
    else:
        # Remove specific attribute set if quantity is 0
        if attributes in cart[item_id]["items_by_attributes"]:
            del cart[item_id]["items_by_attributes"][attributes]

        # Remove entire item if no attributes left
        if not cart[item_id]["items_by_attributes"]:
            del cart[item_id]

    request.session['cart'] = cart
    messages.success(request, f'Updated quantity of {stock.name} in your cart!')

    return redirect(reverse('view_cart'))


def remove_from_cart(request, item_id, item_attribute):
    """ Remove a specific item from the cart by its attribute """

    print("Inside remove_from_cart function. item_id:", item_id, "item_attribute:", item_attribute)

    stock = get_object_or_404(Stock, pk=item_id)
    item_id = str(item_id)

    try:
        cart = request.session.get('cart', {})

        print("Current cart contents:", cart)

        if item_id in cart:
            if item_attribute in cart[item_id]['items_by_attributes']:
                del cart[item_id]['items_by_attributes'][item_attribute]
                print(f"Removed {item_attribute} from item {item_id}")

                if not cart[item_id]['items_by_attributes']:
                    del cart[item_id]
                    print(f"Removed entire item {item_id} as it has no attributes left")

                messages.success(request, f'{stock.name} removed from your cart!')
            else:
                messages.error(request, f'Attribute {item_attribute} not found in cart.')
        else:
            messages.error(request, f'Item {stock.name} not found in cart.')

        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({"status": "success"})

    except Exception as e:
        print(f"Error in remove_from_cart: {e}")
        messages.error(request, f'Error removing item: {e}')
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
