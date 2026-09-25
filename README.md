# Unit tests using Pytest example

Цей репозиторій показує приклад покриття частини коду юніт-тестами мовою python з використанням бібліотеки pytest

---

## Structure

* `order.py` — основний модуль із логікою моделей (`MenuItem`, `OrderItem`, `PricingConfig`, `FoodOrder`).
* `test_order.py` — повний набір юніт-тестів на `pytest`.

## Requirements

* Python 3.10+
* `pytest`

## Installing requirements:
```bash
pip install pytest
```

## Running Tests:
```bash
pytest test_order.py -v
```

## Usage Example:
```bash
from order import MenuItem, OrderItem, FoodOrder, PricingConfig

# Створення позицій меню
burger = MenuItem(code="B1", name="Burger", price=150.50)
cola = MenuItem(code="C1", name="Cola", price=40.00)

# Ініціалізація замовлення
order = FoodOrder()

# Додавання позицій
order.add_item(OrderItem(menu_item=burger, quantity=2))
order.add_item(OrderItem(menu_item=cola, quantity=1))

# Застосування промокоду
order.apply_promo("FOOD10")

# Отримання підсумкових значень
print(f"Subtotal: {order.subtotal()}")  # 341.0
print(f"Total: {order.total()}")        # 322.25
```
