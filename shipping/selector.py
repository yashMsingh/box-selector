from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from .models import Box


@dataclass
class ProductDimensions:
    length_cm: Decimal
    width_cm: Decimal
    height_cm: Decimal
    weight_kg: Decimal

    def sorted_dims(self) -> tuple[Decimal, Decimal, Decimal]:
        """Return (small, mid, large) sorted ascending."""
        dims = sorted([self.length_cm, self.width_cm, self.height_cm])
        return (dims[0], dims[1], dims[2])


@dataclass
class OrderPayload:
    items: list[tuple[ProductDimensions, int]]  # (product_dims, quantity)

    def total_weight_kg(self) -> Decimal:
        """Sum of weight_kg * quantity for all items."""
        total = Decimal('0')
        for product_dims, quantity in self.items:
            total += product_dims.weight_kg * Decimal(quantity)
        return total

    def all_units(self) -> list[ProductDimensions]:
        """Expand items by quantity — returns flat list of ProductDimensions."""
        units = []
        for product_dims, quantity in self.items:
            for _ in range(quantity):
                units.append(product_dims)
        return units


@dataclass
class SelectionResult:
    recommended_box: Optional[Box]
    reason: str
    total_weight_kg: Decimal
    total_volume_cm3: Decimal
    box_volume_cm3: Optional[float]
    fits: bool


def dims_fit_in_box(product: ProductDimensions, box: Box) -> bool:
    """
    Check if a single product unit physically fits inside the box.
    Both product dims and box internal dims are sorted ascending before comparing.
    """
    ps, pm, pl = product.sorted_dims()
    box_dims = sorted([
        box.internal_length_cm,
        box.internal_width_cm,
        box.internal_height_cm,
    ])
    bs, bm, bl = box_dims[0], box_dims[1], box_dims[2]
    return ps <= bs and pm <= bm and pl <= bl


def select_box(payload: OrderPayload) -> SelectionResult:
    """
    Select the cheapest box that fits all items in the order.

    Algorithm:
      1. Compute order totals (weight and volume).
      2. Load all boxes ordered by cost ascending.
      3. For each box, check weight and per-unit dimension constraints.
      4. Return the first box that satisfies both checks.
    """
    # STEP 1 — Compute order totals
    total_weight = payload.total_weight_kg()
    units = payload.all_units()
    total_volume = sum(
        unit.length_cm * unit.width_cm * unit.height_cm
        for unit in units
    )

    # STEP 2 — Load candidate boxes
    boxes = list(Box.objects.all().order_by('cost'))
    if not boxes:
        return SelectionResult(
            recommended_box=None,
            fits=False,
            reason="No boxes available in the system.",
            total_weight_kg=total_weight,
            total_volume_cm3=total_volume,
            box_volume_cm3=None,
        )

    # STEP 3 — Iterate cheapest-first and apply both checks
    for box in boxes:
        # CHECK A — Weight check
        if total_weight > box.max_weight_kg:
            continue

        # CHECK B — Per-unit dimension check
        all_fit = all(dims_fit_in_box(unit, box) for unit in units)
        if not all_fit:
            continue

        # STEP 5 — Both checks passed; return this box
        return SelectionResult(
            recommended_box=box,
            fits=True,
            reason=f"Best fit: {box.name} at cost {box.cost}",
            total_weight_kg=total_weight,
            total_volume_cm3=total_volume,
            box_volume_cm3=box.internal_volume_cm3,
        )

    # STEP 4 — No box passed
    return SelectionResult(
        recommended_box=None,
        fits=False,
        reason="No available box can fit this order. Consider splitting the order.",
        total_weight_kg=total_weight,
        total_volume_cm3=total_volume,
        box_volume_cm3=None,
    )
