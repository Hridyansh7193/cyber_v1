import pytest
from execution.utils.output_parser import OutputParser

def test_parse_json_valid():
    raw = '{"key": "value"}\n{"key2": "value2"}'
    res = OutputParser.parse_json(raw)
    assert len(res) == 2
    assert res[0]["key"] == "value"

def test_parse_json_invalid():
    raw = '{"key": "value"}\ninvalid json\n{"key2": "value2"}'
    res = OutputParser.parse_json(raw)
    assert len(res) == 2
    assert res[1]["key2"] == "value2"

def test_parse_json_empty():
    assert OutputParser.parse_json("") == []

def test_parse_lines():
    raw = "line1\nline2\n\nline3 "
    res = OutputParser.parse_lines(raw)
    assert len(res) == 3
    assert res[0] == "line1"
    assert res[2] == "line3"

def test_parse_lines_empty():
    assert OutputParser.parse_lines("") == []
    assert OutputParser.parse_lines("   \n  \n ") == []

def test_parse_json_nested_structures():
    raw = '{"key": {"nested": "value"}}\n[1, 2, 3]'
    res = OutputParser.parse_json(raw)
    assert len(res) == 2
    assert res[0]["key"]["nested"] == "value"
    assert res[1][0] == 1

def test_parse_json_duplicate_objects():
    raw = '{"id": 1}\n{"id": 1}'
    res = OutputParser.parse_json(raw)
    assert len(res) == 2
    assert res[0] == res[1]

def test_parse_invalid_utf8():
    # Pass a string containing characters that look like bad unicode
    raw = '{"key": "\ud800"}'
    res = OutputParser.parse_json(raw)
    assert len(res) == 1

def test_parse_json_empty_lines_inside():
    raw = '{"key": "value"}\n\n{"key2": "value2"}'
    res = OutputParser.parse_json(raw)
    assert len(res) == 2
