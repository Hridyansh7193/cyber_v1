from enum import Enum

class SearchEntityType(str, Enum):
    FINDINGS = "findings"
    REPORTS = "reports"
    SESSIONS = "sessions"
    URLS = "urls"
    SUBDOMAINS = "subdomains"
    SECRETS = "secrets"
