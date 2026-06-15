# Box Selector — AI-Assisted Shipping Box Recommendation API

A Django REST API that recommends the most cost-efficient shipping box
for an ecommerce order, based on product dimensions and weight.
Includes a modern, interactive single-page frontend.

---

## The Problem

When a warehouse team packs an order, they need to know which box to use.
Choosing manually is slow and error-prone. This system automates it:
given a list of products and quantities, it returns the cheapest box
that physically fits all items and can carry the total weight.

---

## How the Selection Algorithm Works

The algorithm runs two checks against each box, cheapest-first:

1. **Weight check** — total order weight must not exceed the box's
   maximum weight capacity.

2. **Dimension check (per unit, with rotation)** — for each individual
   product unit, its three dimensions are sorted ascending and compared
   against the box's sorted internal dimensions. A product fits if every
   sorted dimension is ≤ the corresponding box dimension. This accounts
   for any rotation of the product.

3. **Selection** — the first box that passes both checks is recommended.
   Because boxes are queried cheapest-first, the result is always the
   most cost-efficient valid option.

> **Design note:** This is a per-unit fit check, not a 3D bin-packing
> solution. It answers: "Can each item physically pass through the
> opening of this box?" — which is the practical warehouse question.
> True bin-packing (can all items fit simultaneously) is an NP-hard
> problem and overkill for most ecommerce SKU sizes.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 4.2 |
| API | Django REST Framework 3.14 |
| Database | SQLite (dev) |
| Testing | pytest + pytest-django |
| Language | Python 3.11+ |
| Frontend | Vanilla JS, HTML5, CSS3 |

---

## Project Structure

```
box_selector/
├── box_selector/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shipping/
│   ├── admin.py                # Django admin registrations
│   ├── models.py               # Product, Box, Order, OrderItem
│   ├── serializers.py          # DRF serializers
│   ├── selector.py             # Core box selection algorithm
│   ├── views.py                # API views
│   ├── urls.py                 # API routes
│   ├── fixtures/
│   │   └── initial_data.json   # Seed data (5 products, 6 boxes)
│   ├── templates/
│   │   └── shipping/
│   │       └── index.html      # Single-page frontend UI
│   └── tests/
│       ├── test_selector.py    # 12 unit tests — algorithm only
│       ├── test_api.py         # 14 API tests — endpoints
│       └── test_integration.py # 25 integration tests — full stack
├── conftest.py
├── pytest.ini
├── requirements.txt
├── AI_USAGE.md
├── TEST_OUTPUT.md
└── README.md
```

---

## Local Setup

### 1. Clone and install

```bash
git clone https://github.com/yashMsingh/box-selector.git
cd box-selector
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Open .env and set a SECRET_KEY value
```

### 3. Run migrations and seed data

```bash
python manage.py migrate
python manage.py loaddata shipping/fixtures/initial_data.json
```

### 4. Start the server

```bash
python manage.py runserver
```

API is live at `http://localhost:8000/api/`
The Frontend UI is live at `http://localhost:8000/`

---

## API Reference

### Health Check

```
GET /health/
```
```json
{"status": "ok", "service": "box-selector-api"}
```

---

### List Products

```
GET /api/products/
```

Returns all products ordered by name.

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "27-inch Monitor",
    "length_cm": "65.00",
    "width_cm": "40.00",
    "height_cm": "10.00",
    "weight_kg": "5.50"
  }
]
```

---

### List Boxes

```
GET /api/boxes/
```

Returns all boxes ordered by cost (cheapest first).

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "XS Box",
    "internal_length_cm": "20.00",
    "internal_width_cm": "15.00",
    "internal_height_cm": "10.00",
    "max_weight_kg": "1.00",
    "cost": "15.00",
    "internal_volume_cm3": 3000.0
  }
]
```

---

### Recommend Box ⭐

```
POST /api/recommend/
Content-Type: application/json
```

**Request:**
```json
{
  "order_reference": "ORD-001",
  "items": [
    {"product_id": 3, "quantity": 1},
    {"product_id": 1, "quantity": 2}
  ]
}
```

**Response 200 — box found:**
```json
{
  "order_reference": "ORD-001",
  "recommended_box": {
    "id": 3,
    "name": "M Box",
    "internal_length_cm": "50.00",
    "internal_width_cm": "35.00",
    "internal_height_cm": "20.00",
    "max_weight_kg": "8.00",
    "cost": "40.00",
    "internal_volume_cm3": 35000.0
  },
  "fits": true,
  "reason": "Best fit: M Box at cost 40.00",
  "total_weight_kg": "1.30",
  "total_volume_cm3": "270.00",
  "box_volume_cm3": 35000.0
}
```

**Response 200 — no box fits:**
```json
{
  "order_reference": "ORD-002",
  "recommended_box": null,
  "fits": false,
  "reason": "No available box can fit this order. Consider splitting the order.",
  "total_weight_kg": "1000.00",
  "total_volume_cm3": "125.00",
  "box_volume_cm3": null
}
```

**Response 400 — validation error:**
```json
{
  "items": "Product with id 9999 does not exist."
}
```

---

## Running Tests

```bash
# Run all 51 tests
pytest --tb=short -v

# Run with coverage report
pip install pytest-cov
pytest --cov=shipping --cov-report=term-missing

# Run a specific suite
pytest shipping/tests/test_selector.py -v
pytest shipping/tests/test_api.py -v
pytest shipping/tests/test_integration.py -v
```

**Test breakdown:**

| Suite | Focus | Count |
|---|---|---|
| test_selector.py | Algorithm logic only, no HTTP | 12 |
| test_api.py | DRF endpoints, serializers | 14 |
| test_integration.py | Full stack, boundary conditions | 25 |
| **Total** | | **51** |

---

## Design Decisions

**Why per-unit dimension check instead of bin packing?**
3D bin packing is NP-hard. For typical ecommerce (single or few SKUs
per order), checking whether each individual product fits through the
box is the correct practical question — and explainable to warehouse
staff. A bin packing solver would add complexity with minimal real
benefit for this use case.

**Why always return HTTP 200 from /api/recommend/?**
A "no box fits" result is a valid business outcome, not a server error.
The `fits` boolean and `reason` field communicate the outcome clearly.
HTTP 4xx/5xx is reserved for malformed requests and server failures.

**Why cheapest-first selection?**
Minimising box cost is the most common business objective. Boxes are
queried `ORDER BY cost ASC`, so the first match is always optimal.
Changing the objective (e.g. smallest volume) requires only changing
the query ordering in `selector.py`.

**Why SQLite?**
This is a hiring assignment. SQLite requires zero infrastructure and
works identically to PostgreSQL for this use case. Switching to
Postgres requires changing one block in settings.py and adding
psycopg2 to requirements.txt — nothing else changes.
