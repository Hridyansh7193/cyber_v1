from urllib.parse import urlparse
from typing import Dict, Any, Optional
from schemas.target import TargetState
from datetime import datetime, timezone

class TargetService:
    """Validates targets and configurations."""
    
    @staticmethod
    def validate_domain(domain: str) -> str:
        if not domain:
            raise ValueError("Domain cannot be empty.")
        if "://" in domain:
            parsed = urlparse(domain)
            domain = parsed.netloc or parsed.path
        if not domain or "." not in domain:
            raise ValueError(f"Invalid domain format: {domain}")
        return domain.lower()

    @staticmethod
    def normalize_target(domain: str, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> TargetState:
        valid_domain = TargetService.validate_domain(domain)
        return TargetState(
            session_id=session_id,
            domain=valid_domain,
            start_time=datetime.now(timezone.utc)
        )
