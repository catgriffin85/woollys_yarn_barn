def format_cart_attributes(size, weight, colour):
    """
    Format attributes consistently for cart keys.
    """
    size = (size or 'None').strip().lower()
    weight = (weight or 'None').strip().lower()
    colour = (colour or 'None').strip().lower()
    return f"{size}-{weight}-{colour}"