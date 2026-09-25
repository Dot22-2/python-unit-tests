from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MenuItem:
    code: str
    name: str
    price: float  # у грошах, не в копійках для простоти

    def __post_init__(self):
        if not self.code:
            raise ValueError("code is required")
        if not self.name:
            raise ValueError("name is required")
        if self.price <= 0:
            raise ValueError("price must be > 0")


@dataclass
class OrderItem:
    menu_item: MenuItem
    quantity: int = 1

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("quantity must be > 0")

    @property
    def line_total(self) -> float:
        return round(self.menu_item.price * self.quantity, 2)


@dataclass
class PricingConfig:
    service_fee_percent: float = 5.0  # 5% сервісний збір
    promo_discounts: Dict[str, int] = field(default_factory=lambda: {
        "FOOD10": 10,
        "FREE100": 100,
        "SPRING5": 5
    })

    def get_promo_percent(self, code: str) -> Optional[int]:
        if code is None:
            return None
        return self.promo_discounts.get(code.strip().upper())


class FoodOrder:
    def __init__(self, pricing: Optional[PricingConfig] = None):
        self.pricing = pricing or PricingConfig()
        self.items: List[OrderItem] = []
        self.applied_promo: Optional[str] = None

    def add_item(self, order_item: OrderItem):
        if not isinstance(order_item, OrderItem):
            raise TypeError("order_item must be OrderItem")

        # мерджимо, якщо вже є така страва
        for it in self.items:
            if it.menu_item.code == order_item.menu_item.code:
                it.quantity += order_item.quantity
                return

        self.items.append(order_item)

    def remove_item(self, code: str):
        before = len(self.items)
        self.items = [it for it in self.items if it.menu_item.code != code]
        if len(self.items) == before:
            raise ValueError("item not found")

    def subtotal(self) -> float:
        return round(sum(it.line_total for it in self.items), 2)

    def apply_promo(self, code: str):
        if not code or not code.strip():
            raise ValueError("promo code must be non-empty")

        percent = self.pricing.get_promo_percent(code)
        if percent is None:
            raise ValueError("invalid promo code")

        if percent < 0 or percent > 100:
            raise ValueError("configured promo out of range 0..100")

        self.applied_promo = code.strip().upper()

    def service_fee_amount(self, base: float) -> float:
        if self.pricing.service_fee_percent < 0 or self.pricing.service_fee_percent > 100:
            raise ValueError("service fee out of range 0..100")
        return round(base * self.pricing.service_fee_percent / 100.0, 2)

    def total(self) -> float:
        base = self.subtotal()
        # сервісний збір
        fee = self.service_fee_amount(base)
        total = base + fee

        # застосувати промо
        if self.applied_promo:
            percent = self.pricing.get_promo_percent(self.applied_promo)
            discount = round(total * percent / 100.0, 2)
            total = total - discount

        if total < 0:
            total = 0.0

        return round(total, 2)


