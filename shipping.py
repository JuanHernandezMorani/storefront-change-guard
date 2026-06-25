FREE_SHIPPING_THRESHOLD_CENTS = 5_000

def calculate_shipping(subtotal_cents: int) -> int:
    if subtotal_cents >= FREE_SHIPPING_THRESHOLD_CENTS:
        return 0
    return 700
