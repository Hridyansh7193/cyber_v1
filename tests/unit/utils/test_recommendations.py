from utils.recommendations import get_recommendation

def test_recommendation_precedence():
    # 1. trusted tool/parser remediation
    meta = {"info": {"remediation": "Do something specific!"}}
    assert get_recommendation("xss_vuln", "xss", meta) == "Do something specific!"
    
    # 2. template-specific mapping
    meta = {"extracted-results": ["X-Frame-Options"]}
    assert get_recommendation("missing-security-headers", None, meta) == "Ensure the server sends the following headers: X-Frame-Options"
    
    # 3. category-specific mapping
    meta = {}
    assert get_recommendation("some-xss-template", None, meta) == "Implement context-aware output encoding and a strong Content-Security-Policy."
    assert get_recommendation(None, "xss", meta) == "Implement context-aware output encoding to prevent XSS."
    
    # 4. None
    assert get_recommendation(None, None, {}) is None
