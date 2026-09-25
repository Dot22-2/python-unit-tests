import pytest
from order import MenuItem, OrderItem, FoodOrder, PricingConfig


def test_menu_item_validation():
    # MenuItem без коду
    with pytest.raises(ValueError, match="code is required"):
        MenuItem(code="", name="Burger", price=100.0)

    # MenuItem без імені
    with pytest.raises(ValueError, match="name is required"):
        MenuItem(code="B1", name="", price=100.0)

    # MenuItem з ціною ≤ 0
    with pytest.raises(ValueError, match="price must be > 0"):
        MenuItem(code="B1", name="Burger", price=0)
    with pytest.raises(ValueError, match="price must be > 0"):
        MenuItem(code="B1", name="Burger", price=-5)


def test_order_item_validation():
    item = MenuItem(code="B1", name="Burger", price=100.0)

    # OrderItem з кількістю ≤ 0
    with pytest.raises(ValueError, match="quantity must be > 0"):
        OrderItem(menu_item=item, quantity=0)
    with pytest.raises(ValueError, match="quantity must be > 0"):
        OrderItem(menu_item=item, quantity=-2)


def test_add_item_type_error():
    order = FoodOrder()
    # FoodOrder.add_item(...) не з OrderItem
    with pytest.raises(TypeError, match="order_item must be OrderItem"):
        order.add_item("Just a string instead of OrderItem")

def test_add_multiple_items_and_subtotal():
    order = FoodOrder()
    item1 = MenuItem(code="B1", name="Burger", price=150.50)
    item2 = MenuItem(code="C1", name="Cola", price=40.00)

    order.add_item(OrderItem(item1, 2))  # 150.50 * 2 = 301.0
    order.add_item(OrderItem(item2, 1))  # 40.0 * 1 = 40.0

    # додати кілька різних позицій → правильний subtotal()
    assert order.subtotal() == 341.0


def test_merge_same_items():
    order = FoodOrder()
    item = MenuItem(code="B1", name="Burger", price=100.0)

    # додати ту саму позицію → кількість мерджиться
    order.add_item(OrderItem(item, 2))
    order.add_item(OrderItem(item, 3))

    assert len(order.items) == 1
    assert order.items[0].quantity == 5
    assert order.subtotal() == 500.0


def test_remove_item():
    order = FoodOrder()
    item = MenuItem(code="B1", name="Burger", price=100.0)
    order.add_item(OrderItem(item, 1))

    # видалити позицію → зменшується сума
    order.remove_item("B1")
    assert len(order.items) == 0
    assert order.subtotal() == 0.0

    # видалити неіснуючу → ValueError
    with pytest.raises(ValueError, match="item not found"):
        order.remove_item("NOT_EXIST")



def test_total_with_service_fee():
    # сервісний збір застосовується (дефолт 5%)
    order = FoodOrder()
    item = MenuItem(code="B1", name="Burger", price=200.0)
    order.add_item(OrderItem(item, 1))

    # subtotal = 200, fee = 10, total = 210
    assert order.total() == 210.0


def test_total_with_promo_and_service_fee():
    order = FoodOrder()
    item = MenuItem(code="B1", name="Burger", price=200.0)
    order.add_item(OrderItem(item, 1))

    # промокод застосовується після сервісного збору (валідний → знижка)
    order.apply_promo("FOOD10")  # 10% знижки
    # Total before promo = 210.0
    # Знижка 10% від 210.0 = 21.0
    # Total = 210.0 - 21.0 = 189.0
    assert order.total() == 189.0


def test_apply_invalid_promo():
    order = FoodOrder()

    # невалідний (пустий) → ValueError
    with pytest.raises(ValueError, match="promo code must be non-empty"):
        order.apply_promo("")

    # невалідний (неіснуючий) → ValueError
    with pytest.raises(ValueError, match="invalid promo code"):
        order.apply_promo("FAKE_PROMO")

def test_promo_config_out_of_range():
    # промокод з конфігурацією >100% → ValueError
    config = PricingConfig(promo_discounts={"CRAZY150": 150})
    order = FoodOrder(pricing=config)

    with pytest.raises(ValueError, match="configured promo out of range 0..100"):
        order.apply_promo("CRAZY150")

    # промокод з конфігурацією <0% → ValueError
    config_negative = PricingConfig(promo_discounts={"MINUS10": -10})
    order_neg = FoodOrder(pricing=config_negative)

    with pytest.raises(ValueError, match="configured promo out of range 0..100"):
        order_neg.apply_promo("MINUS10")


def test_service_fee_out_of_range():
    # сервісний збір >100% → ValueError
    config = PricingConfig(service_fee_percent=150.0)
    order = FoodOrder(pricing=config)
    order.add_item(OrderItem(MenuItem(code="T1", name="Tea", price=50.0), 1))

    with pytest.raises(ValueError, match="service fee out of range 0..100"):
        order.total()

    # сервісний збір <0% → ValueError
    config_neg = PricingConfig(service_fee_percent=-5.0)
    order_neg = FoodOrder(pricing=config_neg)
    order_neg.add_item(OrderItem(MenuItem(code="T1", name="Tea", price=50.0), 1))

    with pytest.raises(ValueError, match="service fee out of range 0..100"):
        order_neg.total()