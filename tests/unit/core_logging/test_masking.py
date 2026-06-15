import pytest
from core_logging.masking import mask_string, mask_sensitive_data

def test_mask_string_jwt():
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    assert mask_string(jwt) == "******** (JWT masked)"

def test_mask_string_bearer():
    bearer = "Bearer 1234567890abcdef"
    assert mask_string(bearer) == "Bearer ********"

def test_mask_string_generic():
    generic = "1234567890abcdef"
    assert mask_string(generic) == "1234********cdef"
    
    short = "short"
    assert mask_string(short) == "********"

def test_mask_sensitive_data_dict():
    data = {
        "user": "admin",
        "password": "supersecretpassword",
        "API_KEY": "1234567890abcdef",
        "nested": {
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    }
    
    masked = mask_sensitive_data(data)
    assert masked["user"] == "admin"
    assert masked["password"] == "supe********word"
    assert masked["API_KEY"] == "1234********cdef"
    assert masked["nested"]["token"] == "******** (JWT masked)"

def test_mask_sensitive_data_list():
    data = [
        {"token": "secret_token_123"},
        "normal_string"
    ]
    masked = mask_sensitive_data(data)
    assert masked[0]["token"] == "secr********_123"
    assert masked[1] == "normal_string"
