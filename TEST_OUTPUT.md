# Test Run Output

## Environment
- Python: 3.13.5
- Django: 4.2.30
- djangorestframework: 3.14.x
- pytest: 9.0.2
- pytest-django: 4.12.0

## Command
```bash
pytest shipping/tests/ -v
```

## Results Summary

| Suite | Tests | Passed | Failed | Errors |
|---|---|---|---|---|
| test_selector.py | 12 | 12 | 0 | 0 |
| test_api.py | 14 | 14 | 0 | 0 |
| test_integration.py | 25 | 25 | 0 | 0 |
| **Total** | **51** | **51** | **0** | **0** |

## Full Output

```
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.0.2, pluggy-1.6.0
cachedir: .pytest_cache
django: version: 4.2.30, settings: box_selector.settings (from ini)
rootdir: box_selector
configfile: pytest.ini
plugins: anyio-4.11.0, django-4.12.0, timeout-2.4.0
collecting ... collected 51 items

shipping/tests/test_api.py::test_01_list_products_returns_200 PASSED     [  1%]
shipping/tests/test_api.py::test_02_product_fields_present PASSED        [  3%]
shipping/tests/test_api.py::test_03_list_boxes_returns_200 PASSED        [  5%]
shipping/tests/test_api.py::test_04_boxes_ordered_by_cost PASSED         [  7%]
shipping/tests/test_api.py::test_05_box_fields_include_volume PASSED     [  9%]
shipping/tests/test_api.py::test_06_recommend_returns_200_with_valid_payload PASSED [ 11%]
shipping/tests/test_api.py::test_07_recommend_fits_true_for_valid_order PASSED [ 13%]
shipping/tests/test_api.py::test_08_recommend_returns_fits_false_when_no_box_fits PASSED [ 15%]
shipping/tests/test_api.py::test_09_recommend_weight_too_heavy PASSED    [ 17%]
shipping/tests/test_api.py::test_10_recommend_cheapest_box_selected PASSED [ 19%]
shipping/tests/test_api.py::test_11_recommend_missing_items_field PASSED [ 21%]
shipping/tests/test_api.py::test_12_recommend_empty_items_list PASSED    [ 23%]
shipping/tests/test_api.py::test_13_recommend_invalid_product_id PASSED  [ 25%]
shipping/tests/test_api.py::test_14_recommend_order_reference_echoed PASSED [ 27%]

shipping/tests/test_integration.py::test_int_01_usb_cable_fits_xs_box PASSED [ 29%]
shipping/tests/test_integration.py::test_int_02_keyboard_needs_m_box PASSED [ 31%]
shipping/tests/test_integration.py::test_int_03_monitor_needs_l_box PASSED [ 33%]
shipping/tests/test_integration.py::test_int_04_heavy_brick_needs_l_box_for_weight PASSED [ 35%]
shipping/tests/test_integration.py::test_int_05_usb_plus_mouse_still_xs PASSED [ 37%]
shipping/tests/test_integration.py::test_int_06_three_mice_weight_forces_s_box PASSED [ 39%]
shipping/tests/test_integration.py::test_int_07_keyboard_plus_mouse_needs_m_box PASSED [ 41%]
shipping/tests/test_integration.py::test_int_08_monitor_plus_keyboard_needs_l_box PASSED [ 43%]
shipping/tests/test_integration.py::test_int_09_two_monitors_need_xl_box PASSED [ 45%]
shipping/tests/test_integration.py::test_int_10_usb_plus_brick_needs_l_box_for_weight PASSED [ 47%]
shipping/tests/test_integration.py::test_int_11_exact_weight_boundary PASSED [ 49%]
shipping/tests/test_integration.py::test_int_12_one_gram_over_weight_boundary PASSED [ 50%]
shipping/tests/test_integration.py::test_int_13_exact_dimension_boundary PASSED [ 52%]
shipping/tests/test_integration.py::test_int_14_one_mm_over_dimension PASSED [ 54%]
shipping/tests/test_integration.py::test_int_15_completely_oversized_product PASSED [ 56%]
shipping/tests/test_integration.py::test_int_16_massively_overweight_order PASSED [ 58%]
shipping/tests/test_integration.py::test_int_17_empty_box_catalog PASSED [ 60%]
shipping/tests/test_integration.py::test_int_18_invalid_product_id_returns_400 PASSED [ 62%]
shipping/tests/test_integration.py::test_int_19_zero_quantity_rejected PASSED [ 64%]
shipping/tests/test_integration.py::test_int_20_negative_quantity_rejected PASSED [ 66%]
shipping/tests/test_integration.py::test_int_21_response_always_has_required_keys PASSED [ 68%]
shipping/tests/test_integration.py::test_int_22_total_weight_is_correct PASSED [ 70%]
shipping/tests/test_integration.py::test_int_23_total_volume_is_correct PASSED [ 72%]
shipping/tests/test_integration.py::test_int_24_box_volume_matches_recommended_box PASSED [ 74%]
shipping/tests/test_integration.py::test_int_25_fits_false_has_null_box PASSED [ 76%]

shipping/tests/test_selector.py::test_01_single_tiny_product_fits_xs_box PASSED [ 78%]
shipping/tests/test_selector.py::test_02_single_large_product_fits_l_box PASSED [ 80%]
shipping/tests/test_selector.py::test_03_product_exactly_matching_box_dims_fits PASSED [ 82%]
shipping/tests/test_selector.py::test_04_weight_forces_larger_box PASSED [ 84%]
shipping/tests/test_selector.py::test_05_total_weight_multi_item PASSED  [ 86%]
shipping/tests/test_selector.py::test_06_two_items_same_product PASSED   [ 88%]
shipping/tests/test_selector.py::test_07_two_different_products_require_m_box PASSED [ 90%]
shipping/tests/test_selector.py::test_08_no_boxes_in_db PASSED           [ 92%]
shipping/tests/test_selector.py::test_09_product_too_large_for_all_boxes PASSED [ 94%]
shipping/tests/test_selector.py::test_10_product_too_heavy_for_all_boxes PASSED [ 96%]
shipping/tests/test_selector.py::test_11_cheapest_valid_box_is_selected PASSED [ 98%]
shipping/tests/test_selector.py::test_12_dims_fit_rotated PASSED         [100%]

============================= 51 passed in 2.87s ==============================
```
