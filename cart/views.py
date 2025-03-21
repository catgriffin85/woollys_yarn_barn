from django.shortcuts import render, redirect

def view_cart(request):
    """ A view that renders the cart contents page """
    return render(request, 'cart/cart.html')

def add_to_cart(request, item_id):
    """ Add a quantity of the specified product to the shopping cart and add weight, colour or size if applicable """

    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    weight = request.POST.get('stock_weight', None)
    colour = request.POST.get('stock_colour', None)
    size = request.POST.get('stock_size', None)

    cart = request.session.get('cart', {})

    if item_id not in cart or isinstance(cart[item_id], int):
        cart[item_id] = {}

    # Handle weight
    if weight:
        cart[item_id].setdefault('items_by_weight', {})
        cart[item_id]['items_by_weight'][weight] = cart[item_id]['items_by_weight'].get(weight, 0) + quantity
    else:
        cart[item_id]['quantity'] = cart[item_id].get('quantity', 0) + quantity

    # Handle colour
    if colour:
        cart[item_id].setdefault('items_by_colour', {})
        cart[item_id]['items_by_colour'][colour] = cart[item_id]['items_by_colour'].get(colour, 0) + quantity

    # Handle size
    if size:
        cart[item_id].setdefault('items_by_size', {})
        cart[item_id]['items_by_size'][size] = cart[item_id]['items_by_size'].get(size, 0) + quantity

    request.session['cart'] = cart
    return redirect(redirect_url)
