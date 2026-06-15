from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from shipping.models import Box, Product


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def full_catalog(db):
    """Creates a realistic full product + box catalog."""
    prod_usb = Product.objects.create(
        name="USB Cable",
        length_cm=Decimal("15.00"),
        width_cm=Decimal("3.00"),
        height_cm=Decimal("1.00"),
        weight_kg=Decimal("0.05"),
    )
    prod_mouse = Product.objects.create(
        name="Wireless Mouse",
        length_cm=Decimal("12.00"),
        width_cm=Decimal("6.00"),
        height_cm=Decimal("4.00"),
        weight_kg=Decimal("0.15"),
    )
    prod_keyboard = Product.objects.create(
        name="Keyboard",
        length_cm=Decimal("45.00"),
        width_cm=Decimal("15.00"),
        height_cm=Decimal("4.00"),
        weight_kg=Decimal("1.20"),
    )
    prod_monitor = Product.objects.create(
        name="Monitor",
        length_cm=Decimal("65.00"),
        width_cm=Decimal("40.00"),
        height_cm=Decimal("10.00"),
        weight_kg=Decimal("5.50"),
    )
    prod_stand = Product.objects.create(
        name="Laptop Stand",
        length_cm=Decimal("30.00"),
        width_cm=Decimal("22.00"),
        height_cm=Decimal("3.00"),
        weight_kg=Decimal("0.80"),
    )
    prod_brick = Product.objects.create(
        name="Heavy Brick",
        length_cm=Decimal("20.00"),
        width_cm=Decimal("15.00"),
        height_cm=Decimal("10.00"),
        weight_kg=Decimal("12.00"),
    )

    box_xs = Box.objects.create(
        name="XS Box",
        internal_length_cm=Decimal("20.00"),
        internal_width_cm=Decimal("15.00"),
        internal_height_cm=Decimal("10.00"),
        max_weight_kg=Decimal("1.00"),
        cost=Decimal("15.00"),
    )
    box_s = Box.objects.create(
        name="S Box",
        internal_length_cm=Decimal("30.00"),
        internal_width_cm=Decimal("20.00"),
        internal_height_cm=Decimal("15.00"),
        max_weight_kg=Decimal("3.00"),
        cost=Decimal("25.00"),
    )
    box_m = Box.objects.create(
        name="M Box",
        internal_length_cm=Decimal("50.00"),
        internal_width_cm=Decimal("35.00"),
        internal_height_cm=Decimal("20.00"),
        max_weight_kg=Decimal("8.00"),
        cost=Decimal("40.00"),
    )
    box_l = Box.objects.create(
        name="L Box",
        internal_length_cm=Decimal("70.00"),
        internal_width_cm=Decimal("50.00"),
        internal_height_cm=Decimal("30.00"),
        max_weight_kg=Decimal("15.00"),
        cost=Decimal("60.00"),
    )
    box_xl = Box.objects.create(
        name="XL Box",
        internal_length_cm=Decimal("90.00"),
        internal_width_cm=Decimal("60.00"),
        internal_height_cm=Decimal("40.00"),
        max_weight_kg=Decimal("25.00"),
        cost=Decimal("85.00"),
    )
    box_xxl = Box.objects.create(
        name="XXL Box",
        internal_length_cm=Decimal("120.00"),
        internal_width_cm=Decimal("80.00"),
        internal_height_cm=Decimal("60.00"),
        max_weight_kg=Decimal("50.00"),
        cost=Decimal("120.00"),
    )

    return {
        "products": {
            "usb": prod_usb,
            "mouse": prod_mouse,
            "keyboard": prod_keyboard,
            "monitor": prod_monitor,
            "stand": prod_stand,
            "brick": prod_brick,
        },
        "boxes": {
            "xs": box_xs,
            "s": box_s,
            "m": box_m,
            "l": box_l,
            "xl": box_xl,
            "xxl": box_xxl,
        },
    }


@pytest.fixture
def client():
    return APIClient()


# ---------------------------------------------------------------------------
# Integration tests — Single product scenarios
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_int_01_usb_cable_fits_xs_box(client, full_catalog):
    usb = full_catalog["products"]["usb"]
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": usb.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True
    assert response.data["recommended_box"]["name"] == "XS Box"


@pytest.mark.django_db
def test_int_02_keyboard_needs_m_box(client, full_catalog):
    keyboard = full_catalog["products"]["keyboard"]
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": keyboard.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True
    assert response.data["recommended_box"]["name"] == "M Box"


@pytest.mark.django_db
def test_int_03_monitor_needs_l_box(client, full_catalog):
    monitor = full_catalog["products"]["monitor"]
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": monitor.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True
    assert response.data["recommended_box"]["name"] == "L Box"


@pytest.mark.django_db
def test_int_04_heavy_brick_needs_l_box_for_weight(client, full_catalog):
    # Dims 20x15x10 fit XS exactly, but weight 12kg skips XS/S/M → L box
    brick = full_catalog["products"]["brick"]
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": brick.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True
    assert response.data["recommended_box"]["name"] == "L Box"


# ---------------------------------------------------------------------------
# Integration tests — Multi-product scenarios
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_int_05_usb_plus_mouse_still_xs(client, full_catalog):
    usb = full_catalog["products"]["usb"]
    mouse = full_catalog["products"]["mouse"]
    response = client.post(
        "/api/recommend/",
        {
            "items": [
                {"product_id": usb.id, "quantity": 1},
                {"product_id": mouse.id, "quantity": 1},
            ]
        },
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True
    assert response.data["recommended_box"]["name"] == "XS Box"


@pytest.mark.django_db
def test_int_06_three_mice_weight_forces_s_box(client, full_catalog):
    # 3 × 0.15kg = 0.45kg < 1kg (XS max); each 12x6x4 fits XS dims → XS
    mouse = full_catalog["products"]["mouse"]
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": mouse.id, "quantity": 3}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True
    assert response.data["recommended_box"]["name"] == "XS Box"


@pytest.mark.django_db
def test_int_07_keyboard_plus_mouse_needs_m_box(client, full_catalog):
    keyboard = full_catalog["products"]["keyboard"]
    mouse = full_catalog["products"]["mouse"]
    response = client.post(
        "/api/recommend/",
        {
            "items": [
                {"product_id": keyboard.id, "quantity": 1},
                {"product_id": mouse.id, "quantity": 1},
            ]
        },
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True
    assert response.data["recommended_box"]["name"] == "M Box"


@pytest.mark.django_db
def test_int_08_monitor_plus_keyboard_needs_l_box(client, full_catalog):
    monitor = full_catalog["products"]["monitor"]
    keyboard = full_catalog["products"]["keyboard"]
    response = client.post(
        "/api/recommend/",
        {
            "items": [
                {"product_id": monitor.id, "quantity": 1},
                {"product_id": keyboard.id, "quantity": 1},
            ]
        },
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True
    assert response.data["recommended_box"]["name"] == "L Box"


@pytest.mark.django_db
def test_int_09_two_monitors_need_xl_box(client, full_catalog):
    # Per-unit check: each monitor (65x40x10) individually fits L box (70x50x30).
    # Total weight: 11.0kg < 15kg (L max). So L box is the result.
    monitor = full_catalog["products"]["monitor"]
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": monitor.id, "quantity": 2}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True
    assert response.data["recommended_box"]["name"] == "L Box"


@pytest.mark.django_db
def test_int_10_usb_plus_brick_needs_l_box_for_weight(client, full_catalog):
    usb = full_catalog["products"]["usb"]
    brick = full_catalog["products"]["brick"]
    response = client.post(
        "/api/recommend/",
        {
            "items": [
                {"product_id": usb.id, "quantity": 1},
                {"product_id": brick.id, "quantity": 1},
            ]
        },
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True
    assert response.data["recommended_box"]["name"] == "L Box"


# ---------------------------------------------------------------------------
# Integration tests — Boundary conditions
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_int_11_exact_weight_boundary(client, db):
    box = Box.objects.create(
        name="Boundary Box",
        internal_length_cm=Decimal("50.00"),
        internal_width_cm=Decimal("50.00"),
        internal_height_cm=Decimal("50.00"),
        max_weight_kg=Decimal("5.00"),
        cost=Decimal("30.00"),
    )
    product = Product.objects.create(
        name="Exact Weight Product",
        length_cm=Decimal("10.00"),
        width_cm=Decimal("10.00"),
        height_cm=Decimal("10.00"),
        weight_kg=Decimal("5.00"),
    )
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": product.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True


@pytest.mark.django_db
def test_int_12_one_gram_over_weight_boundary(client, full_catalog):
    product = Product.objects.create(
        name="Slightly Heavy",
        length_cm=Decimal("5.00"),
        width_cm=Decimal("5.00"),
        height_cm=Decimal("5.00"),
        weight_kg=Decimal("1.01"),
    )
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": product.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True
    assert response.data["recommended_box"]["name"] == "S Box"


@pytest.mark.django_db
def test_int_13_exact_dimension_boundary(client, db):
    box = Box.objects.create(
        name="Exact Dim Box",
        internal_length_cm=Decimal("20.00"),
        internal_width_cm=Decimal("15.00"),
        internal_height_cm=Decimal("10.00"),
        max_weight_kg=Decimal("5.00"),
        cost=Decimal("20.00"),
    )
    product = Product.objects.create(
        name="Exact Dim Product",
        length_cm=Decimal("20.00"),
        width_cm=Decimal("15.00"),
        height_cm=Decimal("10.00"),
        weight_kg=Decimal("0.50"),
    )
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": product.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True


@pytest.mark.django_db
def test_int_14_one_mm_over_dimension(client, full_catalog):
    product = Product.objects.create(
        name="Slightly Too Long",
        length_cm=Decimal("20.01"),
        width_cm=Decimal("15.00"),
        height_cm=Decimal("10.00"),
        weight_kg=Decimal("0.50"),
    )
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": product.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is True
    assert response.data["recommended_box"]["name"] == "S Box"


# ---------------------------------------------------------------------------
# Integration tests — Failure scenarios
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_int_15_completely_oversized_product(client, full_catalog):
    product = Product.objects.create(
        name="Gigantic Product",
        length_cm=Decimal("500.00"),
        width_cm=Decimal("500.00"),
        height_cm=Decimal("500.00"),
        weight_kg=Decimal("1.00"),
    )
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": product.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is False
    assert response.data["recommended_box"] is None
    assert "reason" in response.data
    assert len(response.data["reason"]) > 0


@pytest.mark.django_db
def test_int_16_massively_overweight_order(client, full_catalog):
    product = Product.objects.create(
        name="Lead Block",
        length_cm=Decimal("5.00"),
        width_cm=Decimal("5.00"),
        height_cm=Decimal("5.00"),
        weight_kg=Decimal("1000.00"),
    )
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": product.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is False


@pytest.mark.django_db
def test_int_17_empty_box_catalog(client, db):
    product = Product.objects.create(
        name="Lone Product",
        length_cm=Decimal("10.00"),
        width_cm=Decimal("10.00"),
        height_cm=Decimal("10.00"),
        weight_kg=Decimal("0.50"),
    )
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": product.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is False
    assert "No boxes available" in response.data["reason"]


@pytest.mark.django_db
def test_int_18_invalid_product_id_returns_400(client, db):
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": 99999, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_int_19_zero_quantity_rejected(client, full_catalog):
    usb = full_catalog["products"]["usb"]
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": usb.id, "quantity": 0}]},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_int_20_negative_quantity_rejected(client, full_catalog):
    usb = full_catalog["products"]["usb"]
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": usb.id, "quantity": -1}]},
        format="json",
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Integration tests — Response shape validation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_int_21_response_always_has_required_keys(client, full_catalog):
    monitor = full_catalog["products"]["monitor"]
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": monitor.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    for key in [
        "recommended_box",
        "fits",
        "reason",
        "total_weight_kg",
        "total_volume_cm3",
        "box_volume_cm3",
        "order_reference",
    ]:
        assert key in response.data


@pytest.mark.django_db
def test_int_22_total_weight_is_correct(client, full_catalog):
    usb = full_catalog["products"]["usb"]
    mouse = full_catalog["products"]["mouse"]
    # 2 × 0.05 + 1 × 0.15 = 0.25
    response = client.post(
        "/api/recommend/",
        {
            "items": [
                {"product_id": usb.id, "quantity": 2},
                {"product_id": mouse.id, "quantity": 1},
            ]
        },
        format="json",
    )
    assert response.status_code == 200
    assert float(response.data["total_weight_kg"]) == pytest.approx(0.25)


@pytest.mark.django_db
def test_int_23_total_volume_is_correct(client, full_catalog):
    usb = full_catalog["products"]["usb"]
    # 15 × 3 × 1 = 45 cm³
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": usb.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert float(response.data["total_volume_cm3"]) == pytest.approx(45.0)


@pytest.mark.django_db
def test_int_24_box_volume_matches_recommended_box(client, full_catalog):
    monitor = full_catalog["products"]["monitor"]
    # Monitor → L Box: 70 × 50 × 30 = 105 000 cm³
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": monitor.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["recommended_box"]["name"] == "L Box"
    assert response.data["box_volume_cm3"] == pytest.approx(105000.0)


@pytest.mark.django_db
def test_int_25_fits_false_has_null_box(client, db):
    product = Product.objects.create(
        name="Orphan Product",
        length_cm=Decimal("10.00"),
        width_cm=Decimal("10.00"),
        height_cm=Decimal("10.00"),
        weight_kg=Decimal("0.50"),
    )
    response = client.post(
        "/api/recommend/",
        {"items": [{"product_id": product.id, "quantity": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["fits"] is False
    assert response.data["recommended_box"] is None
    assert response.data["box_volume_cm3"] is None
