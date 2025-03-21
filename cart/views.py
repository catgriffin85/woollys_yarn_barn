from django.shortcuts import render, redirect
from django.http import HttpResponse

def view_cart(request):
    """ A view that renders the cart contents page """
    return render(request, 'cart/cart.html')

def add_to_cart(request, item_id):
    """ Add a quantity of the specified product to the shopping cart, considering weight, colour, or size if applicable """

    # Retrieve cart from session or initialize as empty dictionary
    cart = request.session.get('cart', {})

    # Get the quantity from the form, default to 1 if not provided
    quantity = int(request.POST.get('quantity', 1))

    # Get the redirect URL (if exists)
    redirect_url = request.POST.get('redirect_url', '/')

    # Get attributes from POST, default to None if not selected
    weight = request.POST.get('stock_weight', None)
    colour = request.POST.get('stock_colour', None)
    size = request.POST.get('stock_size', None)

    # Create a combined key for size, weight, and colour
    attributes = f"{size or 'None'}-{weight or 'None'}-{colour or 'None'}"

    # Debugging: Print the attribute values
    print(f"Attributes - Weight: {weight}, Colour: {colour}, Size: {size}")

    # If the item is not in the cart, add it with the appropriate attributes
    if item_id not in cart:
        cart[item_id] = {'items_by_attributes': {attributes: quantity}}
    else:
        # Ensure 'items_by_attributes' exists for the item
        if 'items_by_attributes' not in cart[item_id]:
            cart[item_id]['items_by_attributes'] = {}

        # If the attribute combination exists, add the quantity; otherwise, create a new entry
        if attributes in cart[item_id]['items_by_attributes']:
            cart[item_id]['items_by_attributes'][attributes] += quantity
        else:
            cart[item_id]['items_by_attributes'][attributes] = quantity

    # Save the updated cart back to the session
    request.session['cart'] = cart
    request.session.modified = True

    # Debugging: Print the updated cart
    print("Cart after adding item:", cart)

    # Redirect to the specified URL (or home page if no redirect URL is provided)
    return redirect(redirect_url)
