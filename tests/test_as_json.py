"""
This module provides tests for @as_json() decorator.
"""
from .common import *
from flask_json import _normalize_view_tuple, as_json, JsonTestResponse


class TestAsJson(CommonTest):
    # @as_json uses _normalize_view_tuple() internally to convert wrapped view's
    # return value to expected format.
    # This method tests various return values for _normalize_view_tuple().
    def test_normalize_view_tuple(self):
        # Test if view returns (dict, status, headers).
        data, status, headers = _normalize_view_tuple((dict(), 200, []))
        assert_is_instance(data, dict)
        assert_is_instance(status, int)
        assert_is_instance(headers, list)

        data, status, headers = _normalize_view_tuple((dict(), 200, {}))
        assert_is_instance(data, dict)
        assert_is_instance(status, int)
        assert_is_instance(headers, dict)

        # Test if view returns (dict, ).
        data, status, headers = _normalize_view_tuple((dict(), ))
        assert_is_instance(data, dict)
        assert_is_none(status)
        assert_is_none(headers)

        # Test if view returns (dict, headers, status).
        data, status, headers = _normalize_view_tuple((dict(), [], 1))
        assert_is_instance(data, dict)
        assert_is_instance(status, int)
        assert_is_instance(headers, list)

        # Test if view returns (dict, headers).
        data, status, headers = _normalize_view_tuple((dict(), []))
        assert_is_instance(data, dict)
        assert_is_none(status)
        assert_is_instance(headers, list)

        # Test if view returns (dict, status).
        data, status, headers = _normalize_view_tuple((dict(), 2))
        assert_is_instance(data, dict)
        assert_is_instance(status, int)
        assert_is_none(headers)

    # Test common use case: convert dict return value to JSON response.
    def test_simple(self):
        @as_json
        def view1():
            """Doc"""
            return dict(value=1)

        # Just to make sure decorator is correctly wraps a function.
        assert_equals(view1.__doc__, 'Doc')
        assert_equals(view1.__name__, 'view1')

        r = view1()
        assert_is_instance(r, JsonTestResponse)
        assert_equals(r.status_code, 200)
        assert_dict_equal(r.json, {'status': 200, 'value': 1})

    # Test: convert dict return value to JSON response with custom HTTP status.
    def test_status(self):
        @as_json
        def view1():
            return dict(value=1), 401

        r = view1()
        assert_equals(r.status_code, 401)
        assert_dict_equal(r.json, {'status': 401, 'value': 1})

    # Test: convert dict return value to JSON response with custom HTTP header.
    def test_header(self):
        @as_json
        def view1():
            return dict(value=1), dict(MY='hdr')

        r = view1()
        assert_equals(r.status_code, 200)
        assert_dict_equal(r.json, {'status': 200, 'value': 1})

        assert_equals(r.headers.get('Content-Type'), 'application/json')
        assert_true(r.headers.get('Content-Length', type=int) > 0)
        assert_equals(r.headers.get('MY'), 'hdr')

    # Test: convert dict return value to JSON response with custom status
    # and header (combination of above tests).
    def test_status_header(self):
        @as_json
        def view1():
            return dict(value=1), 400, dict(MY='hdr')

        r = view1()
        assert_equals(r.status_code, 400)
        assert_dict_equal(r.json, {'status': 400, 'value': 1})

        assert_equals(r.headers.get('Content-Type'), 'application/json')
        assert_true(r.headers.get('Content-Length', type=int) > 0)
        assert_equals(r.headers.get('MY'), 'hdr')

    # Test: Same as before but different order of values.
    def test_header_status(self):
        @as_json
        def view1():
            return dict(value=1), dict(MY='hdr'), 400

        r = view1()
        assert_equals(r.status_code, 400)
        assert_dict_equal(r.json, {'status': 400, 'value': 1})

        assert_equals(r.headers.get('Content-Type'), 'application/json')
        assert_true(r.headers.get('Content-Length', type=int) > 0)
        assert_equals(r.headers.get('MY'), 'hdr')

    # Test invalid return value.
    # See also comments for _normalize_view_tuple().
    # Here as_json() raises ValueError: Unsupported return value.
    @raises(ValueError)
    def test_invalid(self):
        @as_json
        def view1():
            return object()  # not supported.

        view1()
