from app.core import OrderLine, apply_discount, calculate_subtotal, calculate_total


def test_calculate_subtotal():
    lines = [
        OrderLine(sku="book", quantity=2, unit_price=10.0),
        OrderLine(sku="pen", quantity=3, unit_price=1.5),
    ]
    assert calculate_subtotal(lines) == 24.5


def test_apply_discount():
    assert apply_discount(100.0, 15.0) == 85.0


def test_calculate_total():
    lines = [OrderLine(sku="notebook", quantity=4, unit_price=5.0)]
    assert calculate_total(lines, discount_percent=10.0) == 18.0

