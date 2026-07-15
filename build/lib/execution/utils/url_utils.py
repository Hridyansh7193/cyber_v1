from typing import Any, Optional

def normalize_url(record: Any) -> Optional[str]:
    """
    Extract and normalize a URL from arbitrary parsed plugin records (e.g. Katana, httpx).
    Guarantees that dictionary `repr()` strings or JSON strings never enter the canonical URL collection.
    """
    if not record:
        return None

    extracted_url = None

    if isinstance(record, dict):
        # 1. Check nested request.endpoint (Katana)
        request = record.get("request", {})
        if isinstance(request, dict) and request.get("endpoint"):
            extracted_url = request.get("endpoint")
        # 2. Check top-level url (httpx, standard Katana)
        elif record.get("url"):
            extracted_url = record.get("url")
        # 3. Check endpoint (fallback)
        elif record.get("endpoint"):
            extracted_url = record.get("endpoint")
        # 4. Check host
        elif record.get("host"):
            extracted_url = record.get("host")
    elif isinstance(record, str):
        # Reject stringified python dictionaries
        if record.startswith("{") and record.endswith("}") and ("'" in record or '"' in record):
            return None
        extracted_url = record
    else:
        # Reject unsupported types
        return None

    if not isinstance(extracted_url, str):
        return None

    # Basic normalization & validation
    extracted_url = extracted_url.strip()
    
    # Needs to be a valid HTTP URL for our purposes
    if not extracted_url.lower().startswith("http://") and not extracted_url.lower().startswith("https://"):
        return None

    return extracted_url
