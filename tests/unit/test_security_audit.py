import glob
import re

FORBIDDEN_PATTERNS = [
    r"shell\s*=\s*True",
    r"subprocess\.Popen",
    r"os\.system",
    r"datetime\.utcnow",
    r"\.utcnow\(\)",
    r"uuid1\(\)",
    r"TODO",
    r"FIXME",
    r"HACK",
    r"XXX",
    r"eval\(",
    r"exec\(",
    r"pickle\.loads",
    r"yaml\.load\(",
]

def test_security_audit_no_forbidden_patterns():
    # Only check python files in core logic
    directories = ["api", "cli", "services", "orchestrator", "storage", "reporting", "execution"]
    
    violations = []
    
    for directory in directories:
        for fpath in glob.glob(f"{directory}/**/*.py", recursive=True):
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
                for pattern in FORBIDDEN_PATTERNS:
                    if re.search(pattern, content):
                        # Special allowance for yaml.safe_load, but our pattern is yaml.load(
                        violations.append(f"Found forbidden pattern '{pattern}' in {fpath}")
                        
    assert not violations, "\n".join(violations)

def test_no_prints_in_services_or_api():
    # CLI can print, but services and API cannot
    directories = ["api", "services"]
    violations = []
    
    for directory in directories:
        for fpath in glob.glob(f"{directory}/**/*.py", recursive=True):
            with open(fpath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if re.search(r"\bprint\(", line):
                        violations.append(f"Found print statement in {fpath} on line {i+1}")
                        
    assert not violations, "\n".join(violations)
