import urllib.request
import urllib.error
import socket
from urllib.parse import urlparse
from schemas.target import TargetState

class TargetResolver:
    """Resolves target protocol and updates TargetState."""
    
    def resolve_target(self, state: TargetState) -> TargetState:
        """
        Attempts to resolve the best protocol (HTTPS > HTTP) for the target.
        Returns a new TargetState with updated fields.
        If it's already resolved or has a scheme, it might just verify it.
        """
        # We only resolve if scheme isn't set, but for safety let's always check if not alive
        domain = state.domain
        
        # Strip protocols if present in domain string accidentally
        if domain.startswith("http://"):
            domain = domain[7:]
        elif domain.startswith("https://"):
            domain = domain[8:]
            
        protocols_to_try = [state.scheme] if state.scheme else ["https", "http"]
        
        resolved_url = None
        scheme = None
        alive = False
        port = None
        
        for proto in protocols_to_try:
            test_url = f"{proto}://{domain}"
            try:
                # Use a fast HEAD request
                req = urllib.request.Request(test_url, method="HEAD")
                # Need a custom opener to prevent following redirects automatically if we want to track chain
                # For now, let urlopen follow them but use a short timeout
                response = urllib.request.urlopen(req, timeout=5)
                
                resolved_url = test_url
                scheme = proto
                alive = True
                port = urlparse(test_url).port or (443 if proto == "https" else 80)
                break
            except urllib.error.URLError:
                continue
            except socket.timeout:
                continue
            except Exception:
                continue
                
        return state.model_copy(update={
            "hostname": state.hostname or domain.split(":", 1)[0],
            "resolved_url": resolved_url,
            "scheme": scheme,
            "port": port,
            "alive": alive
        })
