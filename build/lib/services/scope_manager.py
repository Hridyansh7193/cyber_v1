import re
import ipaddress
from typing import List, Optional
from utils.logger import get_logger

logger = get_logger("scope_manager")

class ScopeManager:
    """Manages in-scope and out-of-scope definitions (Regex & CIDR) and filters targets."""
    
    def __init__(self, in_scope: Optional[List[str]] = None, out_of_scope: Optional[List[str]] = None):
        self.in_scope = in_scope or []
        self.out_of_scope = out_of_scope or []
        
        self._compiled_in_scope_regex = []
        self._compiled_out_scope_regex = []
        self._in_scope_cidrs = []
        self._out_scope_cidrs = []
        
        self._compile_patterns()
        
    def _compile_patterns(self):
        for pattern in self.in_scope:
            if self._is_cidr(pattern):
                self._in_scope_cidrs.append(ipaddress.ip_network(pattern, strict=False))
            else:
                try:
                    # Basic wildcard to regex translation for convenience if users provide wildcards
                    if "*" in pattern and not pattern.startswith(".*") and "\\" not in pattern:
                        regex_pattern = pattern.replace(".", "\\.").replace("*", ".*")
                        regex_pattern = f"^{regex_pattern}$"
                    else:
                        regex_pattern = pattern
                    self._compiled_in_scope_regex.append(re.compile(regex_pattern))
                except re.error as e:
                    logger.warning(f"Invalid in-scope regex '{pattern}': {e}")
                    
        for pattern in self.out_of_scope:
            if self._is_cidr(pattern):
                self._out_scope_cidrs.append(ipaddress.ip_network(pattern, strict=False))
            else:
                try:
                    if "*" in pattern and not pattern.startswith(".*") and "\\" not in pattern:
                        regex_pattern = pattern.replace(".", "\\.").replace("*", ".*")
                        regex_pattern = f"^{regex_pattern}$"
                    else:
                        regex_pattern = pattern
                    self._compiled_out_scope_regex.append(re.compile(regex_pattern))
                except re.error as e:
                    logger.warning(f"Invalid out-of-scope regex '{pattern}': {e}")
                    
    def _is_cidr(self, value: str) -> bool:
        if "/" not in value:
            return False
        try:
            ipaddress.ip_network(value, strict=False)
            return True
        except ValueError:
            return False
            
    def _is_ip(self, value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False

    def is_in_scope(self, target: str) -> bool:
        """
        Check if a target is allowed.
        If in_scope rules exist, it MUST match one.
        If out_of_scope rules exist, it MUST NOT match any.
        """
        if not target:
            return False
            
        # 1. Check out of scope first (explicit denies override explicit allows)
        if self._is_ip(target):
            ip_obj = ipaddress.ip_address(target)
            for cidr in self._out_scope_cidrs:
                if ip_obj in cidr:
                    return False
        else:
            for regex in self._compiled_out_scope_regex:
                if regex.search(target):
                    return False
                    
        # 2. If no in_scope definitions, everything not out-of-scope is allowed
        if not self.in_scope:
            return True
            
        # 3. Check in scope
        if self._is_ip(target):
            ip_obj = ipaddress.ip_address(target)
            for cidr in self._in_scope_cidrs:
                if ip_obj in cidr:
                    return True
        else:
            for regex in self._compiled_in_scope_regex:
                if regex.search(target):
                    return True
                    
        return False
        
    def filter_targets(self, targets: List[str]) -> List[str]:
        """Filters a list of targets (domains/IPs), returning only those in-scope."""
        return [t for t in targets if self.is_in_scope(t)]
