def format_cart_attributes(size=None, weight=None, colour=None):
    """
    Only include the attributes the customer actually selected.
    Returns a string key or "default" if none.
    """
    parts = []
    if size:
        parts.append(size.strip().lower())
    if weight:
        parts.append(weight.strip().lower())
    if colour:
        parts.append(colour.strip().lower())
    return "_".join(parts) if parts else "default"
