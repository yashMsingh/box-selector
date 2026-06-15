# AI Usage Disclosure

This project was built with assistance from Claude (Anthropic).
All AI usage is disclosed below as required by the assignment brief.

---

## Tools Used

- **Claude (Anthropic)** — used for code generation across all phases

---

## How the Work Was Divided

The project was structured into 6 phases. For each phase, I wrote a
detailed prompt specifying exact models, fields, algorithm logic, test
cases, and constraints. Claude generated the initial code from those
prompts.

---

## Prompts Given

### Phase 1 — Scaffold & Models
Specified: Django project structure, all 4 models with exact field
types and validation rules, admin configuration, fixture seed data,
and migration file.

### Phase 2 — Selection Algorithm
Specified: exact dataclass names and fields, the full algorithm
logic step-by-step (weight check → dimension check with sorting →
cheapest-first selection), the dims_fit_in_box helper signature,
and all 12 unit test cases with input values and expected outputs.

### Phase 3 — DRF API
Specified: all serializer classes and fields, all 4 views with exact
request/response contracts, URL routing, and 14 API test cases.

### Phase 4 — Integration Tests
Specified: 25 integration test cases covering single products,
multi-product orders, boundary conditions (exact weight, one-mm
over dimension), and failure modes. Also specified TEST_OUTPUT.md
format.

### Phase 5 — Docs & Cleanup
Specified: README structure and content, this AI_USAGE.md,
and .gitignore.

### Phase 6 — Frontend UI
Specified: Single-page HTML/CSS/JS interface, using Django views to serve the template, dark mode CSS variables, full animation definitions, and frontend API fetch logic.

---

## What I Accepted

- Model field definitions (matched my spec exactly)
- Algorithm implementation in selector.py (verified against each
  test case manually before accepting)
- Serializer and view structure (matched the contracts I specified)
- README structure and API reference examples
- Frontend single-page HTML/CSS/JS (matched design constraints)

---

## What I Rejected or Modified

- **Initial migration file:** Claude generated a migration that used
  `models.CharField` for a DecimalField. Corrected manually.

- **select_box algorithm — float comparison bug:** First generated
  version used float arithmetic for weight comparison. Changed to
  Decimal throughout to avoid floating point precision errors on
  boundary values.

- **RecommendBoxView HTTP status on fits=False:** Claude initially
  returned HTTP 404 when no box was found. Changed to HTTP 200
  with fits=False — a "no box fits" result is a business outcome,
  not a server error.

- **test_int_09 assertion:** Claude initially asserted XL Box for
  2 monitors. Corrected after tracing the algorithm — each unit is
  checked individually, so L Box is correct (each monitor fits L
  dims, total weight 11kg < 15kg max).

---

## Mistakes the AI Made

1. **Float vs Decimal:** Used Python float for weight/dimension
   comparisons in the first pass. This causes subtle bugs on boundary
   values (e.g. 1.0000000001 != 1.0 in float arithmetic). Fixed by
   enforcing Decimal throughout selector.py.

2. **Wrong HTTP status on no-match:** Returned HTTP 404 instead of
   200 when no box fits. Fixed in views.py.

3. **Migration field type error:** One DecimalField was generated as
   CharField in the initial migration. Fixed manually.

4. **test_int_09 wrong box predicted:** Incorrectly asserted XL Box
   for 2 monitors. Corrected after manually tracing the per-unit
   dimension check logic.

---

## How I Verified the Final Code

1. **Manually traced the algorithm** for every test case in
   test_selector.py before running — confirmed expected box matches
   algorithm output on paper first.

2. **Ran the full test suite locally** — all 51 tests pass with
   zero warnings.

3. **Checked boundary conditions manually:** confirmed ≤ (not <)
   is used for both weight and dimension comparisons, covering the
   exact-boundary cases in test_int_11 and test_int_13.

4. **Read every generated file before accepting** — no placeholder
   comments, no TODO blocks, no partial implementations left in.

5. **Verified fixture data against algorithm** — confirmed which box
   each seed product should land in and cross-checked with test
   assertions.

---

## My Own Thinking

The key design decisions were mine, not the AI's:

- **Per-unit dimension check over bin packing** — I chose this
  deliberately. Bin packing is NP-hard and unnecessary for typical
  ecommerce order sizes. The warehouse question is "does this product
  fit through the box opening", not "can I simultaneously pack all
  items into the minimum space".

- **Always return HTTP 200 from /recommend/** — fits=False is a
  valid business response, not an error. The AI's first instinct was
  HTTP 404. I corrected this.

- **Cheapest-first ordering** — I decided cost minimisation is the
  right primary objective. Volume-minimisation is a one-line change
  to the query ordering in selector.py.

- **Decimal over float** — I caught the float precision bug and
  mandated Decimal throughout the algorithm.

- **51 test cases across 3 suites** — I wrote every test case
  specification myself (inputs, expected outputs, edge cases).
  Claude only translated them into pytest code.
