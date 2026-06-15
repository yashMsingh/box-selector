from decimal import Decimal

import pytest

from shipping.models import Box
from shipping.selector import OrderPayload, ProductDimensions, SelectionResult, select_box


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def box_set(db):
    """Create the standard 5-box set ordered cheapest to most expensive."""
    xs = Box.objects.create(
        name="XS Box",
        internal_length_cm=Decimal("20.00"),
        internal_width_cm=Decimal("15.00"),
        internal_height_cm=Decimal("10.00"),
        max_weight_kg=Decimal("1.00"),
        cost=Decimal("15.00"),
    )
    s = Box.objects.create(
        name="S Box",
        internal_length_cm=Decimal("30.00"),
        internal_width_cm=Decimal("20.00"),
        internal_height_cm=Decimal("15.00"),
        max_weight_kg=Decimal("3.00"),
        cost=Decimal("25.00"),
    )
    m = Box.objects.create(
        name="M Box",
        internal_length_cm=Decimal("50.00"),
        internal_width_cm=Decimal("35.00"),
        internal_height_cm=Decimal("20.00"),
        max_weight_kg=Decimal("8.00"),
        cost=Decimal("40.00"),
    )
    l = Box.objects.create(
        name="L Box",
        internal_length_cm=Decimal("70.00"),
        internal_width_cm=Decimal("50.00"),
        internal_height_cm=Decimal("30.00"),
        max_weight_kg=Decimal("15.00"),
        cost=Decimal("60.00"),
    )
    xl = Box.objects.create(
        name="XL Box",
        internal_length_cm=Decimal("90.00"),
        internal_width_cm=Decimal("60.00"),
        internal_height_cm=Decimal("40.00"),
        max_weight_kg=Decimal("25.00"),
        cost=Decimal("85.00"),
    )
    return {"xs": xs, "s": s, "m": m, "l": l, "xl": xl}


# ---------------------------------------------------------------------------
# Basic fit tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_01_single_tiny_product_fits_xs_box(box_set):
    product = ProductDimensions(
        length_cm=Decimal("10"),
        width_cm=Decimal("8"),
        height_cm=Decimal("5"),
        weight_kg=Decimal("0.3"),
    )
    payload = OrderPayload(items=[(product, 1)])
    result = select_box(payload)

    assert result.fits is True
    assert result.recommended_box is not None
    assert result.recommended_box.name == "XS Box"


@pytest.mark.django_db
def test_02_single_large_product_fits_l_box(box_set):
    product = ProductDimensions(
        length_cm=Decimal("60"),
        width_cm=Decimal("45"),
        height_cm=Decimal("25"),
        weight_kg=Decimal("10.0"),
    )
    payload = OrderPayload(items=[(product, 1)])
    result = select_box(payload)

    assert result.fits is True
    assert result.recommended_box is not None
    assert result.recommended_box.name == "L Box"


@pytest.mark.django_db
def test_03_product_exactly_matching_box_dims_fits(box_set):
    # Exact XS box internal dimensions — boundary must pass
    product = ProductDimensions(
        length_cm=Decimal("20"),
        width_cm=Decimal("15"),
        height_cm=Decimal("10"),
        weight_kg=Decimal("0.5"),
    )
    payload = OrderPayload(items=[(product, 1)])
    result = select_box(payload)

    assert result.fits is True
    assert result.recommended_box is not None
    assert result.recommended_box.name == "XS Box"


# ---------------------------------------------------------------------------
# Weight constraint tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_04_weight_forces_larger_box(box_set):
    # Dims fit XS (10x10x10 < 20x15x10) but weight 2.5kg > XS max 1kg
    product = ProductDimensions(
        length_cm=Decimal("10"),
        width_cm=Decimal("10"),
        height_cm=Decimal("10"),
        weight_kg=Decimal("2.5"),
    )
    payload = OrderPayload(items=[(product, 1)])
    result = select_box(payload)

    assert result.fits is True
    assert result.recommended_box is not None
    assert result.recommended_box.name == "S Box"


@pytest.mark.django_db
def test_05_total_weight_multi_item(box_set):
    # 3 units × 0.8 kg = 2.4 kg → exceeds XS max (1 kg), fits S (3 kg)
    product = ProductDimensions(
        length_cm=Decimal("5"),
        width_cm=Decimal("5"),
        height_cm=Decimal("5"),
        weight_kg=Decimal("0.8"),
    )
    payload = OrderPayload(items=[(product, 3)])
    result = select_box(payload)

    assert result.fits is True
    assert result.recommended_box is not None
    assert result.recommended_box.name == "S Box"
    assert result.total_weight_kg == Decimal("2.4")


# ---------------------------------------------------------------------------
# Multi-item tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_06_two_items_same_product(box_set):
    # Each unit: 14x10x8 cm → fits XS (20x15x10). Total weight 0.6 kg < 1 kg.
    product = ProductDimensions(
        length_cm=Decimal("14"),
        width_cm=Decimal("10"),
        height_cm=Decimal("8"),
        weight_kg=Decimal("0.3"),
    )
    payload = OrderPayload(items=[(product, 2)])
    result = select_box(payload)

    assert result.fits is True
    assert result.recommended_box is not None
    assert result.recommended_box.name == "XS Box"


@pytest.mark.django_db
def test_07_two_different_products_require_m_box(box_set):
    # Product B dims force M box; total weight 3.5 kg exceeds S max (3 kg)
    product_a = ProductDimensions(
        length_cm=Decimal("12"),
        width_cm=Decimal("8"),
        height_cm=Decimal("6"),
        weight_kg=Decimal("0.5"),
    )
    product_b = ProductDimensions(
        length_cm=Decimal("40"),
        width_cm=Decimal("28"),
        height_cm=Decimal("15"),
        weight_kg=Decimal("3.0"),
    )
    payload = OrderPayload(items=[(product_a, 1), (product_b, 1)])
    result = select_box(payload)

    assert result.fits is True
    assert result.recommended_box is not None
    assert result.recommended_box.name == "M Box"
    assert result.total_weight_kg == Decimal("3.5")


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_08_no_boxes_in_db():
    # Deliberately NOT using box_set — DB has no boxes
    product = ProductDimensions(
        length_cm=Decimal("10"),
        width_cm=Decimal("10"),
        height_cm=Decimal("10"),
        weight_kg=Decimal("1.0"),
    )
    payload = OrderPayload(items=[(product, 1)])
    result = select_box(payload)

    assert result.fits is False
    assert result.recommended_box is None
    assert "No boxes available" in result.reason


@pytest.mark.django_db
def test_09_product_too_large_for_all_boxes(box_set):
    product = ProductDimensions(
        length_cm=Decimal("200"),
        width_cm=Decimal("200"),
        height_cm=Decimal("200"),
        weight_kg=Decimal("1.0"),
    )
    payload = OrderPayload(items=[(product, 1)])
    result = select_box(payload)

    assert result.fits is False
    assert result.recommended_box is None
    assert "No available box" in result.reason


@pytest.mark.django_db
def test_10_product_too_heavy_for_all_boxes(box_set):
    product = ProductDimensions(
        length_cm=Decimal("5"),
        width_cm=Decimal("5"),
        height_cm=Decimal("5"),
        weight_kg=Decimal("100.0"),
    )
    payload = OrderPayload(items=[(product, 1)])
    result = select_box(payload)

    assert result.fits is False
    assert result.recommended_box is None


@pytest.mark.django_db
def test_11_cheapest_valid_box_is_selected(box_set):
    # Tiny product fits all boxes — must return the cheapest (XS)
    product = ProductDimensions(
        length_cm=Decimal("10"),
        width_cm=Decimal("8"),
        height_cm=Decimal("5"),
        weight_kg=Decimal("0.2"),
    )
    payload = OrderPayload(items=[(product, 1)])
    result = select_box(payload)

    assert result.fits is True
    assert result.recommended_box is not None
    assert result.recommended_box.name == "XS Box"
    assert result.recommended_box.cost == Decimal("15.00")


@pytest.mark.django_db
def test_12_dims_fit_rotated(box_set):
    # XS box internal: 20x15x10 cm. Product given as 10x20x15 (rotated order).
    # Rotation logic must sort both sets of dims and still match XS box.
    product = ProductDimensions(
        length_cm=Decimal("10"),
        width_cm=Decimal("20"),
        height_cm=Decimal("15"),
        weight_kg=Decimal("0.5"),
    )
    payload = OrderPayload(items=[(product, 1)])
    result = select_box(payload)

    assert result.fits is True
    assert result.recommended_box is not None
    assert result.recommended_box.name == "XS Box"
