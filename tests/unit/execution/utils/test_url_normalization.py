from execution.utils.url_utils import normalize_url


def test_katana_record_normalizes_to_endpoint_url():
    record = {
        "timestamp": "2026-07-15T00:00:00Z",
        "request": {
            "method": "GET",
            "endpoint": "http://localhost:3000/api/users"
        },
        "response": {
            "status_code": 200
        }
    }
    assert normalize_url(record) == "http://localhost:3000/api/users"


def test_dict_repr_never_enters_recon_urls():
    record = "{'timestamp': '2026-07-15', 'request': {'endpoint': 'http://localhost:3000'}}"
    assert normalize_url(record) is None


def test_json_object_string_never_enters_recon_urls():
    record = '{"timestamp": "2026", "url": "http://test.com"}'
    assert normalize_url(record) is None


def test_graphql_discovery_receives_clean_url():
    record = {"url": "http://graphql.localhost/api"}
    assert normalize_url(record) == "http://graphql.localhost/api"


def test_swagger_discovery_receives_clean_url():
    record = {"endpoint": "https://api.test.com/v1"}
    assert normalize_url(record) == "https://api.test.com/v1"


def test_normalize_url_returns_none_for_missing_keys():
    assert normalize_url({"random": "data"}) is None


def test_normalize_url_returns_none_for_non_http():
    assert normalize_url("ftp://localhost") is None
    assert normalize_url({"url": "ftp://localhost"}) is None
