from django.shortcuts import get_object_or_404
from stock.models import Stock
from decimal import Decimal
from django.conf import settings


WEIGHT_FRIENDLY_NAMES = {
    'aran': 'Aran',
    'dk': 'Double Knit (DK)',
    'chunky': 'Chunky',
    'super_chunky': 'Super Chunky',
}

COLOUR_FRIENDLY_NAMES = {
    'yellow': 'Yellow',
    'green': 'Green',
    'blue': 'Blue',
    'pink': 'Pink',
    'white': 'White',
    'black': 'Black',
    'grey': 'Grey',
}


def cart_contents(request):
    cart_items = []
    total = Decimal(0)
    stock_count = 0
    cart_items_count = 0


    # Get cart from session
    cart = request.session.get('cart', {})

    for item_id, item_data in cart.items():
        stock = get_object_or_404(Stock, pk=item_id)

        # If the item is not using attributes
        if isinstance(item_data, int):
            total += item_data * stock.price
            stock_count += item_data
            cart_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'stock': stock,
                'price': stock.price,
            })
            cart_items_count += item_data

        else:
            # If the item has attributes like size, colour, or weight
            if 'items_by_attributes' in item_data:
                for attributes, quantity in item_data['items_by_attributes'].items():
                    # Split the attribute key into size, colour, weight
                    size, weight, colour = attributes.split('-')

                    friendly_weight = WEIGHT_FRIENDLY_NAMES.get(weight, weight)
                    friendly_colour = COLOUR_FRIENDLY_NAMES.get(colour, colour)
                    
                    total += quantity * stock.price
                    stock_count += quantity
                    cart_items.append({
                        'item_id': item_id,
                        'quantity': quantity,
                        'stock': stock,
                        'size': size if size != 'None' else None,
                        'colour': friendly_colour if colour != 'None' else None,
                        'weight': friendly_weight if weight != 'None' else None,
                        'price': stock.price,
                    })
                    cart_items_count += quantity


    # Calculate delivery cost
    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = Decimal(0)
        free_delivery_delta = Decimal(0)

    grand_total = delivery + total

    # Ensure decimal places are rounded correctly
    total = total.quantize(Decimal('0.01'))
    delivery = delivery.quantize(Decimal('0.01'))
    grand_total = grand_total.quantize(Decimal('0.01'))

    context = {
        'cart_items': cart_items,
        'total': total,
        'stock_count': stock_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
        'cart_items_count': cart_items_count,
    }

    return context
