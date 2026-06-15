from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from shipping.models import Box, Product


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_products(db):
    p1 = Product.objects.create(
        name="Pen",
        length_cm=Decimal("15.00"),
        width_cm=Decimal("1.00"),
        height_cm=Decimal("1.00"),
        weight_kg=Decimal("0.01"),
    )
    p2 = Product.objects.create(
        name="Notebook",
        length_cm=Decimal("25.00"),
        width_cm=Decimal("18.00"),
        height_cm=Decimal("2.00"),
        weight_kg=Decimal("0.30"),
    )
    p3 = Product.objects.create(
        name="Heavy Brick",
        length_cm=Decimal("20.00"),
        width_cm=Decimal("10.00"),
        height_cm=Decimal("8.00"),
        weight_kg=Decimal("9.00"),
    )
    return {"p1": p1, "p2": p2, "p3": p3}


@pytest.fixture
def sample_boxes(db):
    b1 = Box.objects.create(
        name="Tiny Box",
        internal_length_cm=Decimal("16.00"),
        internal_width_cm=Decimal("2.00"),
        internal_height_cm=Decimal("2.00"),
        max_weight_kg=Decimal("0.50"),
        cost=Decimal("10.00"),
    )
    b2 = Box.objects.create(
        name="Medium Box",
        internal_length_cm=Decimal("30.00"),
        internal_width_cm=Decimal("20.00"),
        internal_height_cm=Decimal("10.00"),
        max_weight_kg=Decimal("5.00"),
        cost=Decimal("35.00"),
    )
    b3 = Box.objects.create(
        name="Heavy Box",
        internal_length_cm=Decimal("30.00"),
        internal_width_cm=Decimal("20.00"),
        internal_height_cm=Decimal("10.00"),
        max_weight_kg=Decimal("15.00"),
        cost=Decimal("55.00"),
    )
    return {"b1": b1, "b2": b2, "b3": b3}


# ---------------------------------------------------------------------------
# GET /api/products/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_01_list_products_returns_200(api_client, sample_products):
    response = api_client.get('/api/products/')
    assert response.status_code == 200
    assert len(response.data) == 3


@pytest.mark.django_db
def test_02_product_fields_present(api_client, sample_products):
    response = api_client.get('/api/products/')
    assert response.status_code == 200
    first = response.data[0]
    for key in ['id', 'name', 'length_cm', 'width_cm', 'height_cm', 'weight_kg']:
        assert key in first


# ---------------------------------------------------------------------------
# GET /api/boxes/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_03_list_boxes_returns_200(api_client, sample_boxes):
    response = api_client.get('/api/boxes/')
    assert response.status_code == 200
    assert len(response.data) == 3


@pytest.mark.django_db
def test_04_boxes_ordered_by_cost(api_client, sample_boxes):
    response = api_client.get('/api/boxes/')
    assert response.status_code == 200
    assert response.data[0]['cost'] == '10.00'


@pytest.mark.django_db
def test_05_box_fields_include_volume(api_client, sample_boxes):
    response = api_client.get('/api/boxes/')
    assert response.status_code == 200
    assert 'internal_volume_cm3' in response.data[0]


# ---------------------------------------------------------------------------
# POST /api/recommend/
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_06_recommend_returns_200_with_valid_payload(api_client, sample_products, sample_boxes):
    p1 = sample_products['p1']
    payload = {
        'order_reference': 'ORD-T01',
        'items': [{'product_id': p1.id, 'quantity': 1}],
    }
    response = api_client.post('/api/recommend/', payload, format='json')
    assert response.status_code == 200
    for key in ['recommended_box', 'fits', 'reason', 'total_weight_kg', 'total_volume_cm3']:
        assert key in response.data


@pytest.mark.django_db
def test_07_recommend_fits_true_for_valid_order(api_client, sample_products, sample_boxes):
    p1 = sample_products['p1']
    payload = {
        'order_reference': 'ORD-T02',
        'items': [{'product_id': p1.id, 'quantity': 1}],
    }
    response = api_client.post('/api/recommend/', payload, format='json')
    assert response.status_code == 200
    assert response.data['fits'] is True
    assert response.data['recommended_box'] is not None


@pytest.mark.django_db
def test_08_recommend_returns_fits_false_when_no_box_fits(api_client, sample_products):
    # No boxes in DB — only sample_products loaded
    p1 = sample_products['p1']
    payload = {
        'items': [{'product_id': p1.id, 'quantity': 1}],
    }
    response = api_client.post('/api/recommend/', payload, format='json')
    assert response.status_code == 200
    assert response.data['fits'] is False
    assert response.data['recommended_box'] is None


@pytest.mark.django_db
def test_09_recommend_weight_too_heavy(api_client, sample_products, sample_boxes):
    # Heavy Brick: 20x10x8 cm, 9 kg — only Heavy Box (max 15 kg) fits
    p3 = sample_products['p3']
    payload = {
        'items': [{'product_id': p3.id, 'quantity': 1}],
    }
    response = api_client.post('/api/recommend/', payload, format='json')
    assert response.status_code == 200
    assert response.data['fits'] is True
    assert response.data['recommended_box']['name'] == 'Heavy Box'


@pytest.mark.django_db
def test_10_recommend_cheapest_box_selected(api_client, sample_products, sample_boxes):
    # Pen (15x1x1 cm, 0.01 kg) fits Tiny Box, Medium Box, and Heavy Box — cheapest wins
    p1 = sample_products['p1']
    payload = {
        'items': [{'product_id': p1.id, 'quantity': 1}],
    }
    response = api_client.post('/api/recommend/', payload, format='json')
    assert response.status_code == 200
    assert response.data['recommended_box']['cost'] == '10.00'


@pytest.mark.django_db
def test_11_recommend_missing_items_field(api_client):
    response = api_client.post('/api/recommend/', {}, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_12_recommend_empty_items_list(api_client):
    response = api_client.post('/api/recommend/', {'items': []}, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_13_recommend_invalid_product_id(api_client, db):
    payload = {
        'items': [{'product_id': 99999, 'quantity': 1}],
    }
    response = api_client.post('/api/recommend/', payload, format='json')
    assert response.status_code == 400
    assert 'items' in response.data


@pytest.mark.django_db
def test_14_recommend_order_reference_echoed(api_client, sample_products, sample_boxes):
    p1 = sample_products['p1']
    payload = {
        'order_reference': 'ORD-ECHO-99',
        'items': [{'product_id': p1.id}],
    }
    response = api_client.post('/api/recommend/', payload, format='json')
    assert response.status_code == 200
    assert response.data['order_reference'] == 'ORD-ECHO-99'
