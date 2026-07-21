from schemas.state import ExecutionState
from config.schemas import BugHunterConfig
from agents.deltas import FindingDelta
from schemas.finding import Finding
import uuid
import re

def analyze_intelligence(state: ExecutionState, config: BugHunterConfig) -> FindingDelta:
    inferred_findings = []
    
    # Heuristic 1: JWT + Sequential IDs = Potential IDOR / Insecure Direct Object Reference
    has_jwt = any("jwt" in str(s).lower() for s in state.js_state.secrets) or any("jwt" in str(t).lower() for techs in state.recon_state.tech_stack.values() for t in techs)
    has_sequential_id = any(re.search(r'id=\d{1,4}(&|$)', param) for param in state.recon_state.parameters)
    if has_jwt and has_sequential_id:
        inferred_findings.append(
            Finding(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, "idor_jwt")),
                title="Potential IDOR (JWT + Sequential IDs detected)",
                severity="medium",
                confidence="low",
                evidence="Sequential IDs detected in parameters alongside JWT usage.",
                target=state.target.domain,
                plugin="analyzer_agent",
                source_tool="analyzer_agent",
                tool_version="1.0.0",
                template_id="analyzer_heuristic",
                category="idor",
                references=()
            )
        )
        
    # Heuristic 2: GraphQL Introspection
    if state.api_state.graphql_urls:
        from urllib.parse import urlparse
        urls_str = ", ".join(state.api_state.graphql_urls)
        first_url = state.api_state.graphql_urls[0]
        try:
            target = urlparse(first_url).netloc
        except Exception:
            target = "unknown"
            
        inferred_findings.append(
            Finding(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, "graphql_introspection")),
                title="GraphQL API Exposed",
                severity="info",
                confidence="certain",
                evidence=f"GraphQL endpoints found: {urls_str}",
                url=first_url,
                target=target,
                plugin="analyzer_agent",
                source_tool="analyzer_agent",
                tool_version="1.0.0",
                template_id="analyzer_heuristic",
                category="exposure",
                references=()
            )
        )
        
    # Heuristic 3: Exposed Swagger / OpenAPI
    if state.api_state.swagger_urls:
        from urllib.parse import urlparse
        urls_str = ", ".join(state.api_state.swagger_urls)
        first_url = state.api_state.swagger_urls[0]
        try:
            target = urlparse(first_url).netloc
        except Exception:
            target = "unknown"
            
        inferred_findings.append(
            Finding(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, "swagger_exposed")),
                title="Swagger / OpenAPI Documentation Exposed",
                severity="info",
                confidence="certain",
                evidence=f"Swagger endpoints found: {urls_str}",
                url=first_url,
                target=target,
                plugin="analyzer_agent",
                source_tool="analyzer_agent",
                tool_version="1.0.0",
                template_id="analyzer_heuristic",
                category="exposure",
                references=()
            )
        )

    # Heuristic 4: WordPress + PHP Exposed
    is_wp = any("wordpress" in str(t).lower() for techs in state.recon_state.tech_stack.values() for t in techs)
    has_php_params = any(".php?" in p for p in state.recon_state.parameters)
    if is_wp and has_php_params:
        inferred_findings.append(
            Finding(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, "wp_php_exposed")),
                title="Exposed PHP parameters on WordPress",
                severity="low",
                confidence="medium",
                evidence="WordPress site is exposing direct .php parameters which may bypass routing.",
                target=state.target.domain,
                plugin="analyzer_agent",
                source_tool="analyzer_agent",
                tool_version="1.0.0",
                template_id="analyzer_heuristic",
                category="misconfiguration",
                references=()
            )
        )

    return FindingDelta(findings=tuple(inferred_findings))
