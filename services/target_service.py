from urllib.parse import urlparse
from typing import Dict, Any, Optional
import ipaddress
from schemas.target import TargetState
from datetime import datetime, timezone

class TargetService:
    """Validates targets and configurations."""
    
    @staticmethod
    def validate_domain(domain: str) -> str:
        if not domain:
            raise ValueError("Domain cannot be empty.")
        parsed = urlparse(domain if "://" in domain else f"//{domain}")
        host = parsed.hostname
        if not host:
            raise ValueError(f"Invalid domain format: {domain}")
        if host != "localhost" and "." not in host:
            try:
                ipaddress.ip_address(host)
            except ValueError:
                raise ValueError(f"Invalid domain format: {domain}")
        if parsed.port:
            return f"{host}:{parsed.port}".lower()
        return host.lower()

    @staticmethod
    def normalize_target(domain: str, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> TargetState:
        valid_domain = TargetService.validate_domain(domain)
        parsed = urlparse(domain if "://" in domain else f"//{domain}")
        return TargetState(
            session_id=session_id,
            domain=valid_domain,
            start_time=datetime.now(timezone.utc),
            hostname=parsed.hostname,
            scheme=parsed.scheme or None,
            port=parsed.port,
            resolved_url=domain if parsed.scheme else None,
        )
