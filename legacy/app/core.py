"""Small core business logic used to exercise high-risk changes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderLine:
    sku: str
    quantity: int
    unit_price: float


def calculate_subtotal(lines: list[OrderLine]) -> float:
    """Return the subtotal for an order before discounts and tax."""
    subtotal = 0.0
    for line in lines:
        if line.quantity < 0:
            raise ValueError("quantity cannot be negative")
        if line.unit_price < 0:
            raise ValueError("unit_price cannot be negative")
        subtotal += line.quantity * line.unit_price
    return round(subtotal, 2)


def apply_discount(subtotal: float, discount_percent: float) -> float:
    """Apply a percentage discount to a subtotal."""
    if subtotal < 0:
        raise ValueError("subtotal cannot be negative")
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("discount_percent must be between 0 and 100")
    return round(subtotal * (1 - discount_percent / 100), 2)


def calculate_total(lines: list[OrderLine], discount_percent: float = 0.0) -> float:
    """Calculate the final total for an order."""
    subtotal = calculate_subtotal(lines)
    return apply_discount(subtotal, discount_percent)

