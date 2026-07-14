from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from schemas.correlated_finding import CorrelatedFinding

def correlate(state: ExecutionState, config: BugHunterConfig) -> tuple[CorrelatedFinding, ...]:
    # Group findings by (tool, endpoint, parameter, vulnerability_class)
    # Using O(N) hash map
    grouped = {}
    
    for finding in state.findings:
        vulnerability_class = finding.title.split(" in ")[0] if " in " in finding.title else finding.title
        endpoint = finding.title.split(" in ")[1] if " in " in finding.title else "unknown"
        tool = "unknown"
        parameter = "unknown"
        
        key = (tool, endpoint, parameter, vulnerability_class)
        
        if key not in grouped:
            grouped[key] = {
                "root_cause": vulnerability_class,
                "vulnerability_class": vulnerability_class,
                "affected_assets": set(),
                "evidence": set(),
                "severity": finding.severity,
                "confidence": 1.0 # default to 1.0 or use logic
            }
            
        grouped[key]["affected_assets"].add(endpoint)
        if finding.evidence:
            grouped[key]["evidence"].add(finding.evidence)
            
    results = []
    for group in grouped.values():
        results.append(
            CorrelatedFinding(
                root_cause=group["root_cause"],
                vulnerability_class=group["vulnerability_class"],
                affected_assets=tuple(sorted(group["affected_assets"])),
                evidence=tuple(sorted(group["evidence"])),
                severity=group["severity"],
                confidence=group["confidence"]
            )
        )
        
    return tuple(results)
