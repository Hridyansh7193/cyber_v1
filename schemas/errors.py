from enum import Enum

class ErrorCode(str, Enum):
    # ==========================
    # Plugin Domain (P)
    # ==========================
    MISSING_BINARY = "P1001"
    UNSUPPORTED_VERSION = "P1002"
    MISSING_TEMPLATES = "P1003"
    MISSING_WORDLISTS = "P1004"

    # ==========================
    # Executor Domain (E)
    # ==========================
    TIMEOUT = "E2001"
    NETWORK_FAILURE = "E2002"
    NO_ELIGIBLE_TARGETS = "E4001"

    # ==========================
    # Report & Parser Domain (R)
    # ==========================
    PARSER_FAILURE = "R3001"
    INVALID_JSON = "R3002"
    REPORT_GENERATION_FAILED = "R5001"

    # ==========================
    # Database Domain (D)
    # ==========================
    DB_MIGRATION_FAILED = "D1001"
    DB_LOCK_TIMEOUT = "D1002"

    # ==========================
    # Workspace Domain (W)
    # ==========================
    WORKSPACE_UNWRITABLE = "W1001"
    EVIDENCE_STORAGE_FAILED = "W1002"

    # ==========================
    # Configuration Domain (C)
    # ==========================
    INVALID_CONFIG = "C1001"
    MISSING_API_KEY = "C1002"

class ToolStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

class ScanStatus(str, Enum):
    SUCCESS = "SUCCESS"
    SUCCESS_WITH_WARNINGS = "SUCCESS_WITH_WARNINGS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
