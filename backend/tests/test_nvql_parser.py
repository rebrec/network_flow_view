import pytest
from app.services.nvql_parser import parse_nvql

def test_parse_simple_filter():
    # GIVEN: A simple query string
    query = "src:10.1.1.1 and port:443"

    # WHEN: We parse it
    parsed = parse_nvql(query)

    # THEN: We get a filter dict
    assert parsed["ip_src"] == "10.1.1.1"
    assert parsed["port_dst"] == 443

def test_parse_zone_filter():
    # GIVEN: A zone query
    query = "dst.zone:DMZ and proto:TCP"

    # WHEN: We parse it
    parsed = parse_nvql(query)

    # THEN: We get zone and protocol filters
    assert parsed["dst_zone"] == "DMZ"
    assert parsed["protocol"] == "TCP"

def test_parse_complex_query():
    # GIVEN: A query with exclusions
    query = "src:10.1.1.1 and not proto:UDP"

    # WHEN: We parse it
    parsed = parse_nvql(query)

    # THEN: We handle exclusion (basic implementation for V1)
    assert parsed["ip_src"] == "10.1.1.1"
    assert parsed["exclude_protocol"] == "UDP"
