import re
import hashlib

def sanitize_workspace_target(target: str) -> str:
    """
    Sanitizes a target string to be safe for use as a directory name
    across all platforms (Windows, Linux, macOS).
    
    If the sanitization alters the string (e.g. replacing ':', '/', '\'),
    a short deterministic hash of the original target is appended to
    prevent collisions (e.g. example.com:443 vs example.com_443).
    """
    if not target:
        return "empty_target"

    # Define invalid characters: 
    # Windows reserved chars: < > : " / \ | ? *
    # Plus control chars and whitespace
    # We replace them with underscores.
    
    # First, strip prefixes like http:// or https:// for better readability
    readable_target = target
    if readable_target.startswith("http://"):
        readable_target = readable_target[len("http://"):]
    elif readable_target.startswith("https://"):
        readable_target = readable_target[len("https://"):]
        
    sanitized = re.sub(r'[\<\>\:\"\/\\\|\?\*\s\x00-\x1F]', '_', readable_target)
    
    # Strip leading/trailing underscores and dots (Windows dislikes trailing dots)
    sanitized = sanitized.strip('_.')
    
    # If the string is empty after sanitization, give it a placeholder
    if not sanitized:
        sanitized = "target"
        
    # Bounded length (Windows MAX_PATH limit mitigation)
    if len(sanitized) > 64:
        sanitized = sanitized[:64].strip('_.')

    # If the original target string differs from the sanitized version in a way 
    # that could cause collisions, append a hash of the *canonical* target.
    # We check against the readable target to see if we altered any unsafe chars.
    if sanitized != readable_target:
        # Create an 8-character hash from the original canonical target
        target_hash = hashlib.sha256(target.encode('utf-8')).hexdigest()[:8]
        return f"{sanitized}_{target_hash}"

    return sanitized
