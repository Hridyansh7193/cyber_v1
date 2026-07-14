from typing import Mapping, Any, Optional

def get_recommendation(template_id: Optional[str], category: Optional[str], metadata: Mapping[str, Any]) -> Optional[str]:
    """
    Deterministically return a recommendation based on precedence:
    1. trusted tool/parser remediation
    2. template-specific mapping
    3. category-specific mapping
    4. None
    """
    # 1. Trusted tool/parser remediation
    if metadata:
        info = metadata.get("info", {})
        if isinstance(info, dict) and "remediation" in info:
            return str(info["remediation"])
            
    # 2. Template-specific mapping
    if template_id == "missing-security-headers":
        extracted = metadata.get("extracted-results", [])
        if extracted:
            return f"Ensure the server sends the following headers: {', '.join(extracted)}"
        return "Ensure the server sends the required security headers."
        
    # 3. Category-specific mapping
    if template_id:
        tid = template_id.lower()
        if "xss" in tid or "cross-site scripting" in tid:
            return "Implement context-aware output encoding and a strong Content-Security-Policy."
        if "sqli" in tid or "sql-injection" in tid:
            return "Use parameterized queries or prepared statements for all database operations."
        if "takeover" in tid:
            return "Remove the dangling DNS record or claim the external resource."
            
    if category:
        cat = category.lower()
        if "xss" in cat:
            return "Implement context-aware output encoding to prevent XSS."
            
    # 4. None
    return None
